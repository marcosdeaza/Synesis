"""Validate the separately published full metadata snapshot without merging the pilot."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.core import curate, read_jsonl


def validate(root: Path) -> dict:
    folder = root / "data/research_225"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    permissions = json.loads((folder / manifest["permissions_file"]).read_text(encoding="utf-8"))
    listed = {item["path"] for item in manifest["files"]}
    if listed != {path.name for path in folder.glob("*.jsonl")}:
        raise ValueError("Snapshot JSONL files do not match the manifest")
    if permissions.get("status") != "permission_confirmed_by_project_owner":
        raise ValueError("Missing project-owner permission provenance")
    rows, hashes = [], {}
    for entry in manifest["files"]:
        path = folder / entry["path"]
        if path.parent != folder or path.is_symlink():
            raise ValueError("Snapshot inputs must be regular files in the snapshot directory")
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        group = read_jsonl(path)
        if digest != entry["sha256"] or len(payload) != entry["bytes"] or len(group) != entry["records"]:
            raise ValueError("Snapshot count, size or checksum mismatch: " + entry["path"])
        rows.extend(group)
        hashes[entry["path"]] = digest
    accepted, issues = curate(rows)
    if issues or len(accepted) != manifest["records"] or len(accepted) != permissions["scope"]["records"]:
        raise ValueError("Snapshot validation failed or records were rejected")
    counts = dict(sorted(Counter(row["institution_id"] for row in accepted).items()))
    if counts != manifest["institutions"]:
        raise ValueError("Institution counts do not match the manifest")
    if any(row.get("abstract") is not None for row in accepted):
        raise ValueError("Full snapshot must preserve abstract minimization")
    by_id = {row["id"]: row for row in rows}
    pilot = read_jsonl(root / "data/pilot/rights_cleared.jsonl")
    if any(by_id.get(row["id"]) != row for row in pilot):
        raise ValueError("CC0 pilot is no longer an identical subset of the research snapshot")
    if len(pilot) != manifest["overlap_with_cc0_pilot"]["records"]:
        raise ValueError("Pilot overlap count differs from the manifest")
    return {"snapshot_id": manifest["snapshot_id"], "records": len(accepted),
            "institutions": counts, "issue_count": len(issues), "sha256": hashes,
            "pilot_overlap_records": len(pilot), "repository_unique_records": len(accepted),
            "permissions_status": permissions["status"], "abstracts_distributed": 0}


if __name__ == "__main__":
    result = validate(ROOT)
    (ROOT / "reports/research_225_validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
