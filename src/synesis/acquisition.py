"""Small shared HTTP client for resumable, polite public-document acquisition."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser


class AccessDenied(RuntimeError):
    """An explicit access or robots restriction; never a request to bypass it."""


class InvalidPDF(ValueError):
    pass


class _CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def redirect_request(self, request, fp, code, message, headers, new_url):
        origin = self.client._origin(new_url)
        robots, interval = self.client._policy(origin)
        if robots is not None and not robots.can_fetch(self.client.user_agent, new_url):
            raise AccessDenied(f"robots.txt disallows redirect destination: {new_url}")
        self.client._pause(origin, interval)
        return super().redirect_request(request, fp, code, message, headers, new_url)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class PoliteClient:
    """One client may visit several origins, with separate rate limits per origin."""

    _locks: dict[str, threading.Lock] = {}
    _last: dict[str, float] = {}
    _guard = threading.Lock()

    def __init__(self, min_delay: float = 3.0,
                 contact: str = "https://github.com/marcosdeaza/Synesis",
                 timeout: float = 45.0, retries: int = 2):
        self.min_delay = max(0.5, float(min_delay))
        self.user_agent = f"SynesisResearch/0.2 (+{contact})"
        self.timeout = timeout
        self.retries = retries
        self._robots: dict[str, tuple[urllib.robotparser.RobotFileParser | None, float]] = {}
        self.last_url: str | None = None
        self.last_headers: dict = {}
        self.robots_observations: dict[str, dict] = {}

    @staticmethod
    def _origin(url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Only public HTTP(S) URLs without credentials are accepted")
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))

    def _open(self, request, check_redirects: bool = True):
        if check_redirects:
            return urllib.request.build_opener(_CheckedRedirect(self)).open(request, timeout=self.timeout)
        # Fetching robots may itself redirect to the canonical robots location;
        # avoid recursively requesting a policy to read that same policy.
        return urllib.request.urlopen(request, timeout=self.timeout)

    def _request(self, url: str, max_bytes: int, check_redirects: bool = True) -> bytes:
        request = urllib.request.Request(url, headers={
            "User-Agent": self.user_agent,
            "Accept": "application/json,application/pdf,text/html,text/plain,*/*;q=0.5",
        })
        with self._open(request, check_redirects=check_redirects) as response:
            length = response.headers.get("Content-Length")
            if length and length.isdigit() and int(length) > max_bytes:
                raise ValueError(f"Response exceeds the {max_bytes} byte limit")
            payload = response.read(max_bytes + 1)
            if len(payload) > max_bytes:
                raise ValueError(f"Response exceeds the {max_bytes} byte limit")
            self.last_url = response.geturl()
            self.last_headers = dict(response.headers.items())
            return payload

    def _policy(self, origin: str) -> tuple[urllib.robotparser.RobotFileParser | None, float]:
        if origin in self._robots:
            return self._robots[origin]
        try:
            payload = self._request(origin + "/robots.txt", 1_000_000, check_redirects=False)
        except urllib.error.HTTPError as error:
            # RFC 9309 §2.3.1.3: a 4xx response for robots is "unavailable",
            # not an explicit Disallow rule. A 401/403 for the PDF itself still
            # raises AccessDenied. Never treat a 200 robots Disallow as absent.
            if 400 <= error.code < 500 and error.code != 429:
                self._robots[origin] = (None, self.min_delay)
                self.robots_observations[origin] = {
                    "status": "unavailable_4xx", "http_status": error.code,
                    "url": origin+"/robots.txt", "checked_at": utc_now(),
                    "handling": "RFC9309_2.3.1.3; resources still require public access"}
                return self._robots[origin]
            raise AccessDenied(f"robots.txt could not be reviewed (HTTP {error.code}): {origin}") from error
        except OSError as error:
            raise AccessDenied(f"robots.txt could not be reviewed: {origin}: {error}") from error
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(payload.decode("utf-8", errors="replace").splitlines())
        interval = parser.crawl_delay(self.user_agent) or 0
        rate = parser.request_rate(self.user_agent)
        if rate and rate.requests:
            interval = max(interval, rate.seconds / rate.requests)
        self._robots[origin] = parser, max(self.min_delay, float(interval))
        self.robots_observations[origin] = {"status": "reviewed", "http_status": 200,
            "url": origin+"/robots.txt", "checked_at": utc_now()}
        # robots is a request too: account for it before the first content request.
        with self._guard:
            self._last[origin] = time.monotonic()
        return self._robots[origin]

    def _pause(self, origin: str, interval: float) -> None:
        with self._guard:
            lock = self._locks.setdefault(origin, threading.Lock())
        with lock:
            remaining = interval - (time.monotonic() - self._last.get(origin, 0))
            if remaining > 0:
                time.sleep(remaining)
            self._last[origin] = time.monotonic()

    def get_bytes(self, url: str, max_bytes: int = 12_000_000) -> bytes:
        origin = self._origin(url)
        robots, interval = self._policy(origin)
        if robots is not None and not robots.can_fetch(self.user_agent, url):
            raise AccessDenied(f"robots.txt disallows this URL: {url}")
        for attempt in range(self.retries + 1):
            self._pause(origin, interval)
            try:
                return self._request(url, max_bytes)
            except urllib.error.HTTPError as error:
                if error.code in {401, 403}:
                    raise AccessDenied(f"HTTP {error.code}: {url}") from error
                if error.code not in {429, 500, 502, 503, 504} or attempt == self.retries:
                    raise
                value = error.headers.get("Retry-After", "")
                delay = max(interval, 2 ** (attempt + 2))
                if value.isdigit():
                    delay = max(delay, float(value))
                elif value:
                    try:
                        delay = max(delay, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
                    except (ValueError, TypeError):
                        pass
                if delay > 60:
                    raise AccessDenied(f"Server requests a deferred retry after {delay:.0f}s: {url}") from error
                time.sleep(delay)
            except (TimeoutError, urllib.error.URLError):
                if attempt == self.retries:
                    raise
                time.sleep(max(interval, 2 ** (attempt + 2)))
        raise RuntimeError("Unreachable retry state")

    def get_text(self, url: str) -> str:
        payload = self.get_bytes(url)
        content_type = self.last_headers.get("Content-Type", "")
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip('" ')
        try:
            return payload.decode(charset, errors="replace")
        except LookupError:
            return payload.decode("utf-8", errors="replace")

    def get_json(self, url: str):
        return json.loads(self.get_text(url))

    def download_pdf(self, url: str, destination: Path | str,
                     max_bytes: int = 512_000_000) -> dict:
        destination = Path(destination)
        cached = destination.is_file()
        hasher, size = hashlib.sha256(), 0
        if cached:
            with destination.open("rb") as source:
                first = source.read(1024)
                if b"%PDF-" not in first:
                    raise InvalidPDF("Existing destination is not a PDF; it is preserved for review")
                hasher.update(first)
                size += len(first)
                for chunk in iter(lambda: source.read(1_048_576), b""):
                    hasher.update(chunk)
                    size += len(chunk)
        else:
            origin = self._origin(url)
            robots, interval = self._policy(origin)
            if robots is not None and not robots.can_fetch(self.user_agent, url):
                raise AccessDenied(f"robots.txt disallows this URL: {url}")
            self._pause(origin, interval)
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + ".part")
            request = urllib.request.Request(url, headers={"User-Agent": self.user_agent,
                                                            "Accept": "application/pdf,*/*;q=0.5"})
            try:
                with self._open(request) as response:
                    length = response.headers.get("Content-Length")
                    if length and length.isdigit() and int(length) > max_bytes:
                        raise ValueError(f"PDF exceeds the {max_bytes} byte limit")
                    first = response.read(1024)
                    if b"%PDF-" not in first:
                        raise InvalidPDF("The response is not a PDF; HTML/error responses are not saved as PDFs")
                    with temporary.open("wb") as target:
                        target.write(first)
                        hasher.update(first)
                        size += len(first)
                        for chunk in iter(lambda: response.read(1_048_576), b""):
                            size += len(chunk)
                            if size > max_bytes:
                                raise ValueError(f"PDF exceeds the {max_bytes} byte limit")
                            target.write(chunk)
                            hasher.update(chunk)
                    self.last_url = response.geturl()
                    self.last_headers = dict(response.headers.items())
                if size < 100:
                    raise InvalidPDF("PDF payload is unexpectedly short")
                temporary.replace(destination)
            except urllib.error.HTTPError as error:
                temporary.unlink(missing_ok=True)
                if error.code in {401, 403}:
                    raise AccessDenied(f"HTTP {error.code}: {url}") from error
                raise
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
        return {"sha256": hasher.hexdigest(), "bytes": size,
                "final_url": url if cached else self.last_url or url,
                "download_url": url, "cache_hit": cached,
                "retrieved_at": datetime.fromtimestamp(destination.stat().st_mtime, timezone.utc).isoformat()}
