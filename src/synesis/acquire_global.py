"""Resumable acquisition of the 35 international Synesis records.

Downloads only documents linked by institutional records or specifically verified
institutional search results. No authentication, impersonation or robots bypass.
The historical metadata snapshot is never modified.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.error
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from .acquisition import AccessDenied, InvalidPDF, PoliteClient, utc_now


BASES = {"mit": "https://dspace.mit.edu/server",
         "tu_berlin": "https://api-depositonce.tu-berlin.de/server"}
# Exact URLs returned by primary-source searches, not constructed bitstream IDs.
# See ADQUISICION_GLOBAL.md for the discovery evidence and access limitations.
HKUST_DISCOVERY = {
    "90343bdae8880ec3": {
        "evidence": "https://researchportal.hkust.edu.hk/en/studentTheses/understanding-young-adults-views-on-marriage-fertility-and-gender-2/",
        "doi": "https://doi.org/10.14711/thesis-hdl167723",
        "pdf": [],
    },
    "acf38ac3f05067da": {
        "evidence": "https://researchportal.hkust.edu.hk/en/studentTheses/social-and-political-views-and-consumer-behavior-in-hong-kong/",
        "doi": "https://doi.org/10.14711/thesis-hdl152458",
        "pdf": [],
    },
    "0c1f642576481f66": {
        "evidence": "https://repository.hkust.edu.hk/ir/bitstream/1783.1-152691/1/1783.1-152691.pdf",
        "pdf": ["https://repository.hkust.edu.hk/ir/bitstream/1783.1-152691/1/1783.1-152691.pdf"],
    },
    "37d1ffefc354dd42": {
        "evidence": "https://repository.hkust.edu.hk/ir/bitstream/1783.1-152483/1/1783.1-152483.pdf",
        "pdf": ["https://repository.hkust.edu.hk/ir/bitstream/1783.1-152483/1/1783.1-152483.pdf"],
    },
    "ddfef707718d2e17": {
        "evidence": "https://repository.hkust.edu.hk/ir/bitstream/1783.1-152513/1/1783.1-152513.pdf",
        "pdf": ["https://repository.hkust.edu.hk/ir/bitstream/1783.1-152513/1/1783.1-152513.pdf"],
    },
    "15978be832848fb8": {
        "evidence": "https://sosc.hkust.edu.hk/research_n_facilities/master_theses#2019",
        "pdf": [],
    },
    "757cc9c24da27a4e": {
        "evidence": "https://repository.hkust.edu.hk/ir/bitstream/1783.1-122003/1/991012770769703412.pdf",
        "pdf": ["https://repository.hkust.edu.hk/ir/bitstream/1783.1-122003/1/991012770769703412.pdf"],
    },
    "175e500b197f12cb": {
        "evidence": "https://sosc.hkust.edu.hk/events/revolutionary-dramas-state-hegemony-propagandist-genre-and-divergent-meanings",
        "pdf": [],
    },
    "bfa9b489208216a5": {
        "evidence": "https://sosc.hkust.edu.hk/events/knowledge-elites-and-industrialization-evidence-china-1862-1911",
        "pdf": [],
    },
    "41be23a8d3161841": {
        "evidence": "https://sosc.hkust.edu.hk/research_n_facilities/master_theses#2019",
        "pdf": [],
    },
}
HKUST_ROUTES = (
    "https://repository.hkust.edu.hk/ir/",
    "https://lbezone.hkust.edu.hk/rse/electronic-theses",
    "https://julac-hkust.primo.exlibrisgroup.com/discovery/search?vid=852JULAC_HKUST%3AHKUST",
)
_hkust_access_cache: list[str] | None = None


def redact_ephemeral_url(url: str) -> tuple[str, bool]:
    """Remove signed-link credentials while retaining a useful source URL."""
    parsed = urlparse(url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    sensitive = {"signature", "policy", "key-pair-id", "awsaccesskeyid", "sig",
                 "token", "access_token", "auth_token", "authorization", "jwt",
                 "credential", "credentials", "download_token", "__cf_chl_tk"}
    def ephemeral(key: str) -> bool:
        lowered = key.lower()
        return (lowered in sensitive or lowered.startswith(("x-amz-", "x-goog-"))
                or "signature" in lowered or "token" in lowered)
    found = any(ephemeral(key) for key, _ in pairs)
    if not found:
        return url, False
    # Expiration parameters belong to the same signed request and are omitted
    # too. Unrelated stable parameters such as sequence remain usable.
    safe = [(key, value) for key, value in pairs
            if not ephemeral(key) and key.lower() not in {"expires", "expiry", "exp"}]
    return urlunparse(parsed._replace(query=urlencode(safe))), True


def sanitize_result(result: dict) -> dict:
    """Sanitize URLs in errors/notes as well as successful CDN destinations."""
    def sanitize_text(text: str) -> str:
        def replace(match):
            original = match.group(0)
            url = original.rstrip("),.;]}\\\"'")
            cleaned, _ = redact_ephemeral_url(url)
            return cleaned + original[len(url):]
        return re.sub(r"https?://[^\s]+", replace, text)
    for file in result.get("files", []):
        final, redacted = redact_ephemeral_url(file["final_url"])
        file["final_url"] = final
        file["final_url_redacted"] = bool(file.get("final_url_redacted") or redacted)
        canonical, canonical_redacted = redact_ephemeral_url(file["download_url"])
        file["download_url"] = canonical
        if canonical_redacted:
            file["download_url_redacted"] = True
    result["notes"] = [sanitize_text(note) for note in result.get("notes", [])]
    return result


class DocumentLinks(HTMLParser):
    def __init__(self, base: str):
        super().__init__()
        self.base = base
        self.urls: list[str] = []
        self.licenses: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        data = dict(attrs)
        if tag == "meta" and data.get("name", "").lower() in {
            "citation_pdf_url", "dc.identifier.fulltext", "dc.relation.haspart"}:
            value = data.get("content", "")
            if value:
                self.urls.append(urljoin(self.base, value))
        if tag == "a" and data.get("href"):
            value = urljoin(self.base, data["href"])
            path = urlparse(value).path.lower()
            if path.endswith(".pdf") or re.search(r"/bitstreams/[^/]+/download$", path):
                self.urls.append(value)
            if "creativecommons.org/licenses/" in value:
                self.licenses.append(value)


def values(metadata: dict, key: str) -> list[str]:
    return [entry["value"] for entry in metadata.get(key, []) if entry.get("value")]


def observed_license(row: dict, metadata: dict | None = None) -> str | None:
    candidates = values(metadata or {}, "dc.rights.uri") + values(metadata or {}, "dc.rights")
    if row.get("license"):
        candidates.append(row["license"])
    return next((value for value in candidates
                 if re.match(r"^https?://creativecommons\.org/(licenses|publicdomain)/", value)), None)


def error_status(error: Exception) -> str:
    if isinstance(error, AccessDenied):
        return "robots_disallowed" if "robots" in str(error).lower() else "restricted"
    if isinstance(error, InvalidPDF):
        return "invalid_pdf"
    if isinstance(error, urllib.error.HTTPError) and error.code in {401, 403}:
        return "restricted"
    return "http_error"


def iter_embedded(client: PoliteClient, url: str, name: str):
    """Follow only pagination supplied by a bounded item/bundle response."""
    for _ in range(10):
        response = client.get_json(url)
        yield from response.get("_embedded", {}).get(name, [])
        following = response.get("_links", {}).get("next", {}).get("href")
        if not following:
            return
        url = urljoin(url, following)
    raise ValueError("Item attachment pagination exceeds the ten-page safety bound")


def discover_dspace(row: dict, client: PoliteClient, result: dict) -> list[dict]:
    base = BASES[row["institution_id"]]
    item_url = f"{base}/api/core/items/{row['record_identifier']}"
    result["evidence_url"] = item_url
    metadata = client.get_json(item_url).get("metadata", {})
    rights = values(metadata, "dc.rights.uri") + values(metadata, "dc.rights")
    if rights:
        result["notes"].append("Derechos observados en ficha: " + "; ".join(dict.fromkeys(rights)))
    license_uri = observed_license(row, metadata)
    candidates = []
    for bundle in iter_embedded(client, item_url + "/bundles?size=100", "bundles"):
        name = bundle.get("name", "")
        if name.upper() != "ORIGINAL":
            continue
        linked = bundle.get("_links", {}).get("bitstreams", {}).get("href")
        if not linked:
            continue
        separator = "&" if "?" in linked else "?"
        for stream in iter_embedded(client, linked + separator + "size=100", "bitstreams"):
            filename = stream.get("name", "")
            url = stream.get("_links", {}).get("content", {}).get("href")
            if not url:
                continue
            suffix = Path(filename).suffix.lower()
            if suffix == ".pdf":
                candidates.append({"url": url, "license": license_uri,
                                   "evidence": item_url, "key": stream.get("uuid", stream.get("id", "file"))})
            elif suffix in {".zip", ".csv", ".tsv", ".json", ".jsonl", ".txt", ".ipynb"}:
                result["notes"].append("Anexo no PDF enlazado en el bundle " + name + ": " + url)
    return candidates


def discover_html(row: dict, client: PoliteClient, result: dict) -> list[dict]:
    url = row["source_url"]
    text = client.get_text(url)
    base = client.last_url or url
    parser = DocumentLinks(base)
    parser.feed(text)
    result["evidence_url"] = base
    license_uri = observed_license(row)
    # Restrict attachments to the institutional page's host or a documented
    # institutional repository host. Unrelated bibliography links are excluded.
    allowed = {urlparse(base).hostname, urlparse(url).hostname}
    return [{"url": link, "license": license_uri, "evidence": base,
             "key": hashlib.sha256(link.encode()).hexdigest()[:12]}
            for link in dict.fromkeys(parser.urls)
            if urlparse(link).hostname in allowed and
            (row["institution_id"] != "usp" or
             ("/publico/" in urlparse(link).path and
              urlparse(link).path.startswith(urlparse(url).path.rsplit("/", 1)[0] + "/")))]


def discover_hkust(row: dict, client: PoliteClient, result: dict) -> list[dict]:
    global _hkust_access_cache
    if _hkust_access_cache is None:
        _hkust_access_cache = []
        for route in HKUST_ROUTES:
            try:
                client.get_text(route)
                _hkust_access_cache.append("Ruta bibliotecaria revisada: " + route)
            except Exception as error:
                _hkust_access_cache.append(error_status(error) + ": " + str(error))
    result["notes"].extend(_hkust_access_cache)
    discovery = HKUST_DISCOVERY[row["id"].rsplit(":", 1)[1]]
    result["evidence_url"] = discovery["evidence"]
    result["notes"].append("Búsqueda individual por título en fuentes oficiales HKUST; no se sustituye la tesis por artículos relacionados.")
    candidates = [{"url": url, "license": None, "evidence": discovery["evidence"],
                   "key": hashlib.sha256(url.encode()).hexdigest()[:12]}
                  for url in discovery["pdf"]]
    if discovery.get("doi"):
        result["notes"].append("DOI institucional localizado: " + discovery["doi"])
    # Consult the exact verified portal/department evidence and any specifically
    # identified DOI. Both remain subject to the shared client's robots checks.
    for url in [discovery["evidence"], discovery.get("doi")]:
        if not url or urlparse(url).path.lower().endswith(".pdf"):
            continue
        try:
            text = client.get_text(url)
            final = client.last_url or url
            parser = DocumentLinks(final)
            parser.feed(text)
            for candidate in parser.urls:
                host = urlparse(candidate).hostname or ""
                if host.endswith(".hkust.edu.hk") or host == "repository.ust.hk":
                    candidates.append({"url": candidate, "license": None,
                                       "evidence": url, "key": hashlib.sha256(candidate.encode()).hexdigest()[:12]})
        except Exception as error:
            result["notes"].append(error_status(error) + ": " + str(error))
    return candidates


def acquire_record(row: dict, root: Path, client: PoliteClient) -> dict:
    result = {"record_id": row["id"], "institution_id": row["institution_id"],
              "status": "not_found", "source_url": row["source_url"],
              "retrieved_at": utc_now(), "files": [],
              "evidence_url": row["source_url"], "notes": []}
    candidates = []
    errors: list[str] = []
    try:
        if row["institution_id"] in BASES:
            candidates = discover_dspace(row, client, result)
        elif row["institution_id"] == "usp":
            candidates = discover_html(row, client, result)
        else:
            candidates = discover_hkust(row, client, result)
    except Exception as error:
        errors.append(error_status(error))
        result["notes"].append(error_status(error) + ": " + str(error))
        if row["institution_id"] in BASES:
            # A public landing page is an independent documented route, not a
            # proxy, login, changed identity, or way of fetching a blocked URL.
            try:
                candidates = discover_html(row, client, result)
            except Exception as fallback_error:
                errors.append(error_status(fallback_error))
                result["notes"].append(error_status(fallback_error) + ": " + str(fallback_error))
    seen: set[str] = set()
    for candidate in candidates:
        url = candidate["url"]
        if url in seen:
            continue
        seen.add(url)
        key = re.sub(r"[^a-zA-Z0-9_-]", "", str(candidate["key"]))[:48]
        filename = row["id"].rsplit(":", 1)[1] + "__" + key + ".pdf"
        destination = root / "data/fulltext/pdf" / row["institution_id"] / filename
        try:
            download = client.download_pdf(url, destination)
            from pypdf import PdfReader
            reader = PdfReader(destination)
            pages = len(reader.pages)
            if not pages:
                raise InvalidPDF("PDF parsed with zero pages")
            result["files"].append({
                "path": str(destination.relative_to(root)), "download_url": url,
                "sha256": download["sha256"], "bytes": download["bytes"],
                "final_url": download["final_url"], "source_license": candidate["license"],
                "license_evidence_url": candidate["evidence"], "pages": pages,
            })
        except Exception as error:
            errors.append(error_status(error))
            result["notes"].append(error_status(error) + ": " + str(error))
    if result["files"]:
        result["status"] = "downloaded"
    elif errors:
        result["status"] = next((status for status in ["robots_disallowed", "restricted", "invalid_pdf", "http_error"] if status in errors), "http_error")
    else:
        # Discover_hkust records source errors in notes while continuing distinct
        # institutional evidence routes. Preserve actual blockers in the status.
        for status in ["robots_disallowed", "restricted", "http_error"]:
            if any(note.startswith(status + ":") for note in result["notes"]):
                result["status"] = status
                break
        if not candidates:
            result["notes"].append("No se identificó un enlace PDF público de esta tesis en las fuentes institucionales consultadas.")
    result["retrieved_at"] = utc_now()
    result["robots_observations"] = list(getattr(client, "robots_observations", {}).values())
    return sanitize_result(result)


def save_checkpoint(path: Path, records: dict[str, dict], order: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text("".join(json.dumps(records[key], ensure_ascii=False) + "\n"
                                  for key in order if key in records), encoding="utf-8")
    temporary.replace(path)


def run(root: Path, institutions: set[str] | None = None, *, retry_failures: bool = False,
        min_delay: float = 3.0, contact: str = "https://github.com/marcosdeaza/Synesis") -> dict:
    source = root / "data/research_225/global.jsonl"
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    path = root / "data/fulltext/sources_global.jsonl"
    processed = {record["record_id"]: record for record in
                 (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())} if path.exists() else {}
    client = PoliteClient(min_delay=min_delay, contact=contact)
    order = [row["id"] for row in rows]
    for row in rows:
        if institutions and row["institution_id"] not in institutions:
            continue
        previous = processed.get(row["id"])
        if previous:
            complete = previous["status"] == "downloaded" and all(
                (root / f["path"]).is_file() and
                hashlib.sha256((root / f["path"]).read_bytes()).hexdigest() == f["sha256"]
                for f in previous.get("files", []))
            if complete or (previous["status"] != "downloaded" and not retry_failures):
                continue
        result = acquire_record(row, root, client)
        processed[row["id"]] = result
        save_checkpoint(path, processed, order)
        print(json.dumps({"record_id": row["id"], "institution": row["institution_id"],
                          "status": result["status"], "files": len(result["files"])}, ensure_ascii=False), flush=True)
    return {"records": len(processed), "status": dict(Counter(value["status"] for value in processed.values())),
            "files": sum(len(value["files"]) for value in processed.values())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Adquisición verificable y reanudable de documentos institucionales globales")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--institution", action="append", choices=["mit", "tu_berlin", "hkust", "usp"])
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--min-delay", type=float, default=3.0)
    parser.add_argument("--contact", default="https://github.com/marcosdeaza/Synesis")
    arguments = parser.parse_args()
    result = run(arguments.root.resolve(), set(arguments.institution) if arguments.institution else None,
                 retry_failures=arguments.retry_failures, min_delay=arguments.min_delay, contact=arguments.contact)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
