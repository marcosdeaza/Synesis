"""Validate acquisition evidence without requiring large release assets in Git."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .corpus import load_metadata, verify_pdf

STATUSES = {"downloaded", "restricted", "robots_disallowed", "not_found", "http_error", "invalid_pdf"}
MANIFESTS = ("data/fulltext/sources_spain.jsonl", "data/fulltext/sources_global.jsonl")


def validate_fulltext(root: Path | str, *, require_files=False, require_complete=True) -> dict:
    root = Path(root).resolve()
    metadata, _ = load_metadata(root)
    known = {row["id"]: row for row in metadata}
    sources, paths = {}, set()
    for filename in MANIFESTS:
        path = root / filename
        if not path.exists() and not require_complete:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = row.get("record_id")
            if key not in known or key in sources:
                raise ValueError("unknown_or_duplicate_source_record")
            if row.get("institution_id") != known[key]["institution_id"]:
                raise ValueError("institution_mismatch")
            if row.get("status") not in STATUSES:
                raise ValueError("invalid_source_status")
            if row.get("source_url") != known[key]["source_url"]:
                raise ValueError("source_url_mismatch")
            if not isinstance(row.get("files"), list):
                raise ValueError("invalid_file_list")
            if bool(row["files"]) != (row["status"] == "downloaded"):
                raise ValueError("downloaded_status_file_mismatch")
            for entry in row["files"]:
                value = entry.get("path")
                if not isinstance(value, str) or Path(value).is_absolute():
                    raise ValueError("unsafe_pdf_path")
                resolved = (root / value).resolve()
                expected = root / "data/fulltext/pdf" / row["institution_id"]
                if not resolved.is_relative_to(expected.resolve()) or resolved.suffix.lower() != ".pdf" or value in paths:
                    raise ValueError("unsafe_or_duplicate_pdf_path")
                paths.add(value)
                if not isinstance(entry.get("bytes"), int) or isinstance(entry["bytes"], bool) or entry["bytes"] < 100:
                    raise ValueError("invalid_pdf_size")
                if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
                    raise ValueError("invalid_pdf_sha256")
                if urlsplit(entry.get("download_url", "")).scheme not in {"https", "http"}:
                    raise ValueError("missing_download_provenance")
                if require_files:
                    verify_pdf(root, entry)
                    with resolved.open("rb") as stream:
                        if b"%PDF-" not in stream.read(1024):
                            raise ValueError("invalid_pdf_signature")
            sources[key] = row
    missing = sorted(set(known) - set(sources))
    if require_complete and missing:
        raise ValueError("unattempted_records:" + str(len(missing)))
    institutions = []
    for institution in sorted({row["institution_id"] for row in metadata}):
        group = [row for row in metadata if row["institution_id"] == institution]
        found = [sources[row["id"]] for row in group if row["id"] in sources]
        files = [entry for row in found for entry in row["files"]]
        institutions.append({"institution_id": institution, "metadata_records": len(group),
                             "attempted_records": len(found), "downloaded_records": sum(bool(row["files"]) for row in found),
                             "pdf_files": len(files), "pdf_bytes": sum(entry["bytes"] for entry in files),
                             "statuses": dict(sorted(Counter(row["status"] for row in found).items()))})
    return {"schema_version": "0.2.0", "metadata_records": len(metadata), "attempted_records": len(sources),
            "downloaded_records": sum(row["downloaded_records"] for row in institutions),
            "pdf_files": sum(row["pdf_files"] for row in institutions),
            "pdf_bytes": sum(row["pdf_bytes"] for row in institutions),
            "statuses": dict(sorted(Counter(row["status"] for row in sources.values()).items())),
            "institutions": institutions, "unattempted_record_ids": missing,
            "unavailable": [{"record_id": row["record_id"], "institution_id": row["institution_id"],
                             "status": row["status"], "source_url": row["source_url"], "notes": row.get("notes", [])}
                            for row in sorted(sources.values(), key=lambda row: row["record_id"]) if not row["files"]],
            "interpretation": "Acquisition coverage, not AI adoption or a representative academic sample."}
