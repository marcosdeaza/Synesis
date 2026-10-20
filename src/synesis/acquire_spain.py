"""Resume public full-text acquisition for the fixed 190-record Spanish snapshot.

The historical metadata snapshot is read only. No login, request-a-copy, embargo
bypass or inferred open access is used. PDFs are stored in the local full-text
layer and individually hashed; the manifest is checkpointed after each record.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import threading
import urllib.error
from urllib.parse import parse_qs, quote, unquote, urljoin, urlsplit, urlunsplit
import zipfile

from .acquisition import AccessDenied, InvalidPDF, PoliteClient, utc_now

CONTACT = "https://github.com/marcosdeaza/Synesis"
MAX_BYTES = 512_000_000
FINAL_STATUSES = {"downloaded", "restricted", "not_found", "robots_disallowed", "http_error", "invalid_pdf"}


class ItemLinks(HTMLParser):
    """Read actual download links, signposting and explicit access metadata."""

    def __init__(self, base: str):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.pdf_links: list[str] = []
        self.archive_links: list[str] = []
        self.citation_links: list[str] = []
        self.request_copy_links: list[str] = []
        self.rights: list[str] = []
        self._anchor: dict | None = None

    def _absolute(self, value):
        # Literal spaces/Unicode in published HTML links are URL-encoded, without
        # decoding existing escapes or changing reserved path/query separators.
        parts = urlsplit(urljoin(self.base, value))
        path = quote(parts.path, safe="/%:@-._~!$&'()*+,;=")
        query = quote(parts.query, safe="=&?/:;,%+@-._~!$'()*")
        return urlunsplit((parts.scheme, parts.netloc, path, query, ""))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if tag == "meta":
            name = attrs.get("name", "").casefold()
            value = attrs.get("content", "")
            if name == "citation_pdf_url" and value:
                self.citation_links.append(self._absolute(value))
            elif name in {"dc.rights", "dcterms.rights", "dc.rights.accessrights"} and value:
                self.rights.append(value)
        elif tag == "link" and attrs.get("rel", "").casefold() == "item":
            if attrs.get("type", "").casefold() == "application/pdf":
                self.pdf_links.append(self._absolute(href))
            elif "zip" in attrs.get("type", "").casefold():
                self.archive_links.append(self._absolute(href))
        elif tag == "a":
            self._anchor = {"href": self._absolute(href), "text": [], "pdf": False}
            if "request-a-copy" in href or "request-copy" in href:
                self.request_copy_links.append(self._absolute(href))
        if self._anchor is not None and "file-pdf" in attrs.get("class", ""):
            self._anchor["pdf"] = True

    def handle_data(self, text):
        if self._anchor is not None:
            self._anchor["text"].append(text)

    def handle_endtag(self, tag):
        if tag != "a" or self._anchor is None:
            return
        value = self._anchor
        self._anchor = None
        href, text = value["href"], " ".join(value["text"]).casefold()
        if "/bitstream" not in urlsplit(href).path:
            return
        path = urlsplit(href).path.casefold()
        if value["pdf"] or path.endswith(".pdf") or ".pdf" in text:
            self.pdf_links.append(href)
        elif path.endswith(".zip") or ".zip" in text:
            self.archive_links.append(href)

    @staticmethod
    def _bitstream(url):
        query = parse_qs(urlsplit(url).query)
        if query.get("bitstream"):
            return query["bitstream"][0]
        found = re.search(r"/bitstreams/([^/]+)/", urlsplit(url).path)
        return found[1] if found else None

    def candidates(self):
        denied = {self._bitstream(u) for u in self.request_copy_links}
        denied.discard(None)
        def allowed(values):
            return list(dict.fromkeys(u for u in values if self._bitstream(u) not in denied))
        # Real anchors/signposting avoid duplicate citation aliases in DSpace 6.
        pdf = allowed(self.pdf_links or self.citation_links)
        return pdf, allowed(self.archive_links)


def _error_status(error):
    if isinstance(error, AccessDenied):
        message = str(error).casefold()
        if "robots" in message and "disallow" in message:
            return "robots_disallowed"
        if "could not be reviewed" in message or "deferred retry" in message:
            return "http_error"
        return "restricted"
    if isinstance(error, InvalidPDF):
        return "invalid_pdf"
    if isinstance(error, urllib.error.HTTPError) and error.code in {401, 403}:
        return "restricted"
    if isinstance(error, urllib.error.HTTPError) and error.code == 404:
        return "not_found"
    return "http_error"


def _safe_name(value: str):
    return re.sub(r"[^A-Za-z0-9._-]", "_", value)


def _hash(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def _file_result(root, path, url, result, license_url, evidence_url, **extra):
    path.chmod(0o444)
    return {"path": path.relative_to(root).as_posix(), "download_url": url,
            "sha256": result["sha256"], "bytes": result["bytes"],
            "final_url": result.get("final_url") or url,
            "source_license": license_url, "license_evidence_url": evidence_url,
            **extra}


def _valid_checkpoint(root, row):
    files = row.get("files", [])
    if row.get("status") not in FINAL_STATUSES:
        return False
    if row.get("status") != "downloaded":
        return True
    if not files:
        return False
    for item in files:
        path = root / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or _hash(path) != item["sha256"]:
            return False
    return True


def acquire_record(root: Path, source: dict, client: PoliteClient):
    record_id, institution = source["id"], source["institution_id"]
    page_url = source["source_url"]
    output = {"record_id": record_id, "institution_id": institution, "status": "not_found",
              "source_url": page_url, "retrieved_at": utc_now(), "files": [],
              "evidence_url": page_url, "notes": []}
    work = root / "work/spain_fulltext_pages" / institution
    work.mkdir(parents=True, exist_ok=True)
    try:
        page = client.get_text(page_url)
    except Exception as first_error:
        # Only retry transport/not-found failures on known official identifiers.
        # Explicit robots/HTTP access denials are final, never routed around.
        if isinstance(first_error, AccessDenied) or isinstance(first_error, urllib.error.HTTPError) and first_error.code in {401, 403}:
            output["status"] = _error_status(first_error)
            output["notes"].append(f"GET item page failed: {type(first_error).__name__}: {first_error}")
            return output
        output["notes"].append(f"Initial item GET failed: {type(first_error).__name__}: {first_error}")
        try:
            if institution == "upv":
                handle = source["record_identifier"].rsplit(":", 1)[-1]
                from urllib.parse import quote
                item = client.get_json("https://riunet.upv.es/server/api/pid/find?id=" + quote(handle, safe=""))
                page_url = "https://riunet.upv.es/entities/publication/" + item["uuid"]
            elif institution == "uev":
                # The repository's own OAI Identify declares this .com origin.
                page_url = page_url.replace("https://titula.universidadeuropea.es/", "https://titula.universidadeuropea.com/", 1)
            page = client.get_text(page_url)
            output["notes"].append("Recovered through an alternative official item URL: " + page_url)
        except Exception as error:
            output["status"] = _error_status(error)
            output["notes"].append(f"Official item alternative failed: {type(error).__name__}: {error}")
            return output
    evidence = client.last_url or page_url
    output["evidence_url"] = evidence
    (work / (_safe_name(record_id) + ".html")).write_text(page, encoding="utf-8")
    parser = ItemLinks(evidence)
    parser.feed(page)
    explicit_restrictions = [r for r in parser.rights if re.search(r"restrictedAccess|closedAccess|embargoedAccess", r, re.I)]
    if explicit_restrictions:
        output["status"] = "restricted"
        output["notes"].append("Current item page explicitly declares " + ", ".join(explicit_restrictions) + "; technical download URLs were not requested.")
        return output
    pdf_links, archive_links = parser.candidates()
    output["notes"].append(f"Public item page: {len(pdf_links)} PDF candidate(s), {len(archive_links)} ZIP candidate(s), {len(parser.request_copy_links)} request-a-copy link(s).")
    if parser.request_copy_links:
        output["notes"].append("Request-a-copy files were excluded; no copy request was sent.")
    license_url = next((r for r in parser.rights if re.match(r"https?://(?:www\.)?creativecommons\.org/(?:licenses|publicdomain)/", r)), None)
    if not license_url and source.get("license") and source["license"] in page:
        license_url = source["license"]
    # A missing license is preserved as unknown; HTTP access does not create one.
    target = root / "data/fulltext/pdf" / institution / _safe_name(record_id)
    failures = []
    for number, url in enumerate(pdf_links, 1):
        name = f"{number:02}-{hashlib.sha256(url.encode()).hexdigest()[:14]}.pdf"
        path = target / name
        try:
            used_url = url
            try:
                result = client.download_pdf(url, path)
            except Exception as initial_error:
                # A citation alias is another URL explicitly offered by this same
                # item, never a guessed mirror. Do not route around access denials.
                if isinstance(initial_error, AccessDenied) or isinstance(initial_error, urllib.error.HTTPError) and initial_error.code in {401, 403}:
                    raise
                filename = unquote(urlsplit(url).path.rsplit("/", 1)[-1]).casefold()
                aliases = [candidate for candidate in parser.citation_links if candidate != url
                           and unquote(urlsplit(candidate).path.rsplit("/", 1)[-1]).casefold() == filename]
                if not aliases:
                    raise
                output["notes"].append(f"Initial PDF URL failed: {url}: {type(initial_error).__name__}: {initial_error}; trying its published citation alias.")
                used_url = aliases[0]
                result = client.download_pdf(used_url, path)
            output["files"].append(_file_result(root, path, used_url, result, license_url, evidence))
        except Exception as error:
            failures.append(_error_status(error))
            output["notes"].append(f"PDF candidate failed: {url}: {type(error).__name__}: {error}")
    # Original public ZIPs can be the only available representation of a thesis.
    # Extract only complete PDF members, with generated local paths (no ZipSlip).
    for number, url in enumerate(archive_links, 1):
        try:
            payload = client.get_bytes(url, max_bytes=MAX_BYTES)
            final_url = client.last_url or url
            if not zipfile.is_zipfile(io.BytesIO(payload)):
                raise InvalidPDF("Archive link did not return a valid ZIP")
            archive_hash = hashlib.sha256(payload).hexdigest()
            archive_path = root / "work/spain_fulltext_archives" / (archive_hash + ".zip")
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            if not archive_path.exists():
                archive_path.write_bytes(payload)
            pdf_members = 0
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                members = [m for m in archive.infolist() if not m.is_dir() and m.filename.casefold().endswith(".pdf")]
                if len(members) > 500 or sum(m.file_size for m in members) > 2 * MAX_BYTES:
                    raise ValueError("Public ZIP exceeds the bounded PDF member count/total size")
                for member in members:
                    if member.flag_bits & 1:
                        raise AccessDenied("Encrypted ZIP member; no password or bypass attempted")
                    if member.file_size > MAX_BYTES or member.compress_size and member.file_size / member.compress_size > 500:
                        raise ValueError("Archive PDF member exceeds the safe size/expansion limit")
                    body = archive.read(member)
                    if b"%PDF-" not in body[:1024] or len(body) < 100:
                        failures.append("invalid_pdf")
                        output["notes"].append("Invalid PDF member in public ZIP: " + member.filename)
                        continue
                    digest = hashlib.sha256(body).hexdigest()
                    path = target / f"zip-{number:02}-{digest[:16]}.pdf"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if not path.exists():
                        temporary = path.with_suffix(".pdf.part")
                        temporary.write_bytes(body)
                        temporary.replace(path)
                    result = {"sha256": digest, "bytes": len(body), "final_url": final_url}
                    output["files"].append(_file_result(root, path, url, result, license_url, evidence,
                                                        archive_member=member.filename, archive_sha256=archive_hash))
                    pdf_members += 1
            output["notes"].append(f"Public ZIP: {pdf_members} original PDF member(s) acquired; archive SHA-256 {archive_hash}.")
        except Exception as error:
            failures.append(_error_status(error))
            output["notes"].append(f"ZIP candidate failed: {url}: {type(error).__name__}: {error}")
    if output["files"]:
        # Byte-identical aliases are recorded once per item; files remain untouched.
        unique = {}
        for item in output["files"]:
            if item["sha256"] in unique:
                kept = unique[item["sha256"]]
                output["notes"].append("Byte-identical alias: " + item["download_url"] + "; kept " + kept["path"])
                if item["path"] != kept["path"]:
                    (root / item["path"]).unlink(missing_ok=True)
            else:
                unique[item["sha256"]] = item
        output["files"] = list(unique.values())
        output["status"] = "downloaded"
        if failures or parser.request_copy_links:
            output["notes"].append("Partial item coverage: acquired public PDFs; failed/restricted candidates remain documented above.")
    elif failures:
        output["status"] = next((s for s in ["robots_disallowed", "restricted", "invalid_pdf", "http_error", "not_found"] if s in failures), "http_error")
    elif parser.request_copy_links:
        output["status"] = "restricted"
    else:
        output["status"] = "not_found"
        output["notes"].append("No publicly offered PDF/ZIP found on the current item page; no hidden endpoint or guessed attachment was requested.")
    output["retrieved_at"] = utc_now()
    return output


def run(root: Path, institution="all", limit=None, retry_statuses=(), min_delay=3.0, retry_incomplete=False):
    root = root.resolve()
    rows = [json.loads(line) for line in (root / "data/research_225/spain.jsonl").read_text().splitlines() if line.strip()]
    path = root / "data/fulltext/sources_spain.jsonl"
    previous = {r["record_id"]: r for r in (json.loads(line) for line in path.read_text().splitlines() if line.strip())} if path.exists() else {}
    selected = [r for r in rows if institution == "all" or r["institution_id"] == institution]
    if limit is not None:
        selected = selected[:limit]
    results = dict(previous)
    lock = threading.Lock()
    def checkpoint(result):
        with lock:
            results[result["record_id"]] = result
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".jsonl.part")
            temporary.write_text("".join(json.dumps(results[r["id"]], ensure_ascii=False) + "\n" for r in rows if r["id"] in results), encoding="utf-8")
            temporary.replace(path)
            print(json.dumps({"record_id": result["record_id"], "institution_id": result["institution_id"],
                              "status": result["status"], "files": len(result["files"]),
                              "completed_records": len(results)}, ensure_ascii=False), flush=True)
    def worker(iid):
        client = PoliteClient(min_delay=min_delay, contact=CONTACT)
        for source in selected:
            if source["institution_id"] != iid:
                continue
            old = previous.get(source["id"])
            incomplete = old and any("candidate failed:" in str(note) for note in old.get("notes", []))
            if old and old.get("status") not in retry_statuses and not (retry_incomplete and incomplete) and _valid_checkpoint(root, old):
                continue
            if old and old.get("status") == "downloaded":
                # Never bless changed cached bytes with a newly computed hash.
                # Quarantine a mismatching file so the client must fetch it again.
                for item in old.get("files", []):
                    suspect = root / item["path"]
                    if suspect.is_file() and (suspect.stat().st_size != item["bytes"] or _hash(suspect) != item["sha256"]):
                        quarantine = root / "work/spain_fulltext_corrupt" / (_safe_name(source["id"]) + "-" + suspect.name)
                        quarantine.parent.mkdir(parents=True, exist_ok=True)
                        suspect.replace(quarantine)
            try:
                result = acquire_record(root, source, client)
            except Exception as error:
                result = {"record_id": source["id"], "institution_id": iid, "status": _error_status(error),
                          "source_url": source["source_url"], "retrieved_at": utc_now(), "files": [],
                          "evidence_url": source["source_url"], "notes": [f"Record acquisition failed: {type(error).__name__}: {error}"]}
            checkpoint(result)
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(worker, sorted({r["institution_id"] for r in selected})))
    from collections import Counter
    return {"records_in_snapshot": len(rows), "records_with_status": len(results),
            "status_counts": dict(Counter(r["status"] for r in results.values())),
            "pdfs": sum(len(r["files"]) for r in results.values()),
            "bytes": sum(f["bytes"] for r in results.values() for f in r["files"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--institution", choices=["all", "uev", "upv"], default="all")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry-status", action="append", choices=sorted(FINAL_STATUSES), default=[])
    parser.add_argument("--min-delay", type=float, default=3.0)
    parser.add_argument("--retry-incomplete", action="store_true", help="Recheck public candidates that failed within an otherwise downloaded item")
    args = parser.parse_args()
    print(json.dumps(run(args.root, args.institution, args.limit, args.retry_status, args.min_delay, args.retry_incomplete), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
