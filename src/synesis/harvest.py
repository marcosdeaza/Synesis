"""Bounded OAI-PMH harvesting. No PDF download, bypass or credentials."""
from __future__ import annotations

import hashlib
import json
import math
import unicodedata
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from .core import metadata_date, valid_url

NS = {"o": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/",
      "dim": "http://www.dspace.org/xmlns/dspace/dim"}


def fetch(url: str, user_agent: str, attempts: int = 3, min_interval: float = 0.0) -> bytes:
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": user_agent}), timeout=40) as response:
                if response.headers.get_content_type() not in {"text/xml", "application/xml", "application/octet-stream", "text/plain"}:
                    raise ValueError("Endpoint did not return XML; review the source adapter.")
                return response.read(12_000_001)
        except urllib.error.HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts-1:
                raise
            delay = exc.headers.get("Retry-After", "")
            wait = min(int(delay), 300) if delay.isdigit() else 2 ** (attempt+2)
            time.sleep(max(wait, min_interval))
    raise RuntimeError("Unreachable retry state")


def check_robots(endpoint: str, user_agent: str) -> float:
    parts = urllib.parse.urlsplit(endpoint)
    robots = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    try:
        with urllib.request.urlopen(urllib.request.Request(robots, headers={"User-Agent": user_agent}), timeout=30) as response:
            lines = response.read(1_000_000).decode("utf-8", errors="replace").splitlines()
    except urllib.error.HTTPError as exc:
        if exc.code in {404, 410}:
            return 0.0  # Missing robots does not grant reuse rights.
        raise RuntimeError("Robots unavailable. Stop and review source access.") from exc
    except OSError as exc:
        raise RuntimeError("Robots unavailable. Stop and review source access.") from exc
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(lines)
    if not parser.can_fetch(user_agent, endpoint):
        raise PermissionError("robots.txt disallows this path. No harvest attempted.")
    crawl_delay = parser.crawl_delay(user_agent) or 0
    rate = parser.request_rate(user_agent)
    rate_interval = rate.seconds / rate.requests if rate and rate.requests else 0
    return float(max(crawl_delay, rate_interval))


def _type_token(value: str) -> str:
    value = value.rsplit("/", 1)[-1].strip().casefold()
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)).split())


BACHELOR_TYPES = {"tfg", "bachelor", "bachelorthesis", "bachelor thesis", "bachelor's thesis",
                  "trabajo fin de grado", "trabajo de fin de grado", "treball de fi de grau"}
MASTER_TYPES = {"tfm", "master", "masterthesis", "master thesis", "master's thesis",
                "trabajo fin de master", "trabajo de fin de master", "treball de fi de master"}
DOCTORAL_TYPE = re.compile(r"doctoral|doctorat|doctorado|doutorado|doctor of philosophy|\bph[.]?d[.]?\b", re.I)


def parse_page(payload: bytes, institution_id: str, fetched_at: str) -> tuple[list[dict], str | None]:
    """Read DIM qualifiers when present; leave unqualified Dublin Core dates ambiguous."""
    root = ET.fromstring(payload)
    if root.tag != "{" + NS["o"] + "}OAI-PMH":
        raise ValueError("Response is not an OAI-PMH document.")
    errors = root.findall("o:error", NS)
    if errors:
        if all(error.get("code") == "noRecordsMatch" for error in errors):
            return [], None
        raise ValueError("OAI error: " + "; ".join((e.get("code", "") + ": " + (e.text or "")) for e in errors))
    listing = root.find("o:ListRecords", NS)
    if listing is None:
        raise ValueError("OAI response has no ListRecords element.")
    rows = []
    for record in listing.findall("o:record", NS):
        header = record.find("o:header", NS)
        if header is None or header.get("status") == "deleted":
            continue
        metadata = record.find("o:metadata", NS)
        if metadata is None:
            continue
        fields = [f for f in metadata.findall(".//dim:field", NS) if f.get("mdschema") == "dc"]
        is_dim = bool(fields)
        def values(name: str, qualifier: str | None = "*") -> list[str]:
            if is_dim:
                nodes = [f for f in fields if f.get("element") == name and (qualifier == "*" or f.get("qualifier") == qualifier)]
            else:
                nodes = metadata.findall(f".//dc:{name}", NS)
            return [x.text.strip() for x in nodes if x.text and x.text.strip()]
        def first(name: str, qualifier: str | None = "*") -> str | None:
            found = values(name, qualifier)
            return found[0] if found else None
        titles = values("title", None) if is_dim else values("title")
        types, dates = values("type"), values("date")
        if not titles:
            continue
        degree_text = " | ".join(types)
        if DOCTORAL_TYPE.search(degree_text):
            continue
        tokens = {_type_token(t) for t in types}
        master, bachelor = bool(tokens & MASTER_TYPES), bool(tokens & BACHELOR_TYPES)
        # Conflicting explicit levels need human review rather than a guessed level.
        level = "master" if master and not bachelor else "bachelor" if bachelor and not master else "unknown"
        identifier = header.findtext("o:identifier", default="", namespaces=NS).strip()
        links = [x for x in values("identifier", "uri" if is_dim else "*") if valid_url(x)]
        if not identifier or not links:
            continue
        date = first("date", "issued") if is_dim else (dates[0] if dates else None)
        year, precision = metadata_date(date)
        # Qualified field names express repository semantics, never a verified defense date.
        semantics = "dc_date_issued" if is_dim and date else "unknown" if is_dim else "dc_date_unqualified"
        rights = values("rights")
        license_url = next((v for v in values("rights", "uri") if re.match(r"https?://(?:www[.])?creativecommons[.]org/(?:licenses|publicdomain)/", v)), None)
        rows.append({"id": institution_id+"-"+hashlib.sha256(identifier.encode()).hexdigest()[:16],
            "institution_id": institution_id, "title": titles[0], "abstract": None,
            "issued_raw": date, "year": year, "date_precision": precision,
            "date_semantics": semantics, "date_candidates_raw": dates,
            "date_evidence": ("DIM dc.date.issued" if is_dim else "Unqualified dc.date; first value retained") + ": " + str(date),
            "created_raw": first("date", "created") if is_dim else None,
            "accessioned_raw": first("date", "accessioned") if is_dim else None,
            "degree_level": level, "degree_evidence": "dc.type="+degree_text, "source_url": links[0],
            "record_identifier": identifier, "language": first("language"),
            "subjects": list(dict.fromkeys(values("subject"))), "license": license_url, "rights_raw": rights,
            "rights_statement": next((v for v in rights if "rightsstatements.org/" in v), None),
            "access_rights": first("rights", "accessRights") if is_dim else None,
            "retrieved_at": fetched_at, "evidence_kind": "metadata", "campus": None,
            "campus_evidence_url": None,
            "abstract_available": bool(values("description", "abstract")) if is_dim else bool(values("description")),
            "abstract_omitted_by_policy": True,
            "adapter": "dim_qualified_needs_review" if is_dim else "oai_dc_generic_needs_review"})
    token = listing.find("o:resumptionToken", NS)
    return rows, token.text.strip() if token is not None and token.text else None


def harvest(endpoint: str, institution_id: str, set_spec: str, output: Path, contact: str,
            pages: int = 1, since: str | None = None, until: str | None = None,
            delay: float = 3.0, metadata_prefix: str = "oai_dc") -> dict:
    if not isinstance(pages, int) or isinstance(pages, bool) or not 1 <= pages <= 20 or not math.isfinite(delay) or delay < 2:
        raise ValueError("Use 1..20 pages and at least 2 seconds between requests.")
    if metadata_prefix not in {"oai_dc", "dim"}:
        raise ValueError("Supported metadata prefixes are oai_dc and dim.")
    if output.exists():
        raise FileExistsError("Choose a new snapshot directory; existing harvests are immutable.")
    agent = f"SynesisResearch/0.1 (+{contact})"
    robots_interval = check_robots(endpoint, agent)
    effective_delay = max(delay, robots_interval)
    output.mkdir(parents=True)
    params = {"verb": "ListRecords", "metadataPrefix": metadata_prefix, "set": set_spec}
    if since:
        params["from"] = since
    if until:
        params["until"] = until
    log, records, seen_tokens = [], [], set()
    token, exhausted = None, False
    for index in range(pages):
        if index or robots_interval:
            time.sleep(effective_delay)
        url = endpoint + "?" + urllib.parse.urlencode(params)
        fetched_at = datetime.now(timezone.utc).isoformat()
        payload = fetch(url, agent, min_interval=effective_delay)
        if len(payload) > 12_000_000:
            raise ValueError("Page exceeds 12 MB limit; stop and review endpoint.")
        filename = f"page-{index+1:03}.xml"
        (output/filename).write_bytes(payload)
        page, token = parse_page(payload, institution_id, fetched_at)
        records.extend(page)
        log.append({"url": url, "retrieved_at": fetched_at, "sha256": hashlib.sha256(payload).hexdigest(),
                    "file": filename, "parsed_records": len(page)})
        if not token:
            exhausted = True
            break
        if token in seen_tokens:
            raise ValueError("Repeated resumption token. Stop rather than loop.")
        seen_tokens.add(token)
        params = {"verb": "ListRecords", "resumptionToken": token}
    (output/"metadata.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in records), encoding="utf-8")
    manifest = {"institution_id": institution_id, "endpoint": endpoint, "set": set_spec,
        "metadata_prefix": metadata_prefix, "from": since, "until": until, "filter_semantics": "OAI modification datestamp, not thesis issue date",
        "records": len(records), "exhausted": exhausted, "truncated_by_page_limit": not exhausted,
        "requests": log, "user_agent": agent, "robots_checked": True,
        "robots_min_interval_seconds": robots_interval, "effective_delay_seconds": effective_delay,
        "rights_status": "Review source terms before exporting; no PDF fetched."}
    (output/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return manifest
