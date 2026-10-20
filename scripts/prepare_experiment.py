#!/usr/bin/env python3
"""Prepare deterministic record groups and splits; never labels or trains a model."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re


FIELDS = ("record_id", "institution_id", "group_id", "split", "group_size", "known_pdf_sha_count")


def make_assignments(metadata: list[dict], sources: list[dict], seed: int = 42) -> list[dict]:
    """Union records sharing any PDF SHA before assigning their complete group."""
    records = {row["id"]: row for row in metadata}
    if len(records) != len(metadata):
        raise ValueError("duplicate_metadata_record_id")
    parents = {key: key for key in records}
    pdfs: dict[str, set[str]] = defaultdict(set)

    def find(key: str) -> str:
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parents[max(a, b)] = min(a, b)

    first_seen: dict[str, str] = {}
    seen_records = set()
    for source in sources:
        key = source["record_id"]
        if key not in records or key in seen_records:
            raise ValueError("unknown_or_duplicate_acquisition_record")
        seen_records.add(key)
        for entry in source.get("files", []):
            if Path(entry.get("path", "")).suffix.lower() != ".pdf":
                continue
            digest = entry.get("sha256", "")
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("invalid_pdf_sha256")
            pdfs[key].add(digest)
            if digest in first_seen:
                union(key, first_seen[digest])
            else:
                first_seen[digest] = key
    groups: dict[str, list[str]] = defaultdict(list)
    for key in sorted(records):
        groups[find(key)].append(key)
    assignments = []
    for members in groups.values():
        group_id = "grp_" + hashlib.sha256("\n".join(members).encode()).hexdigest()
        digest = hashlib.sha256(f"synesis-split-v1\0{seed}\0{group_id}".encode()).hexdigest()
        bucket = int(digest, 16) % 10_000
        split = "train" if bucket < 8000 else "validation" if bucket < 9000 else "test"
        known_pdfs = set().union(*(pdfs[key] for key in members))
        for key in members:
            assignments.append({"record_id": key, "institution_id": records[key]["institution_id"],
                                "group_id": group_id, "split": split,
                                "group_size": len(members), "known_pdf_sha_count": len(known_pdfs)})
    return sorted(assignments, key=lambda row: row["record_id"])


def read_input(root: Path, path: Path, *, jsonl: bool = True) -> tuple[list, dict]:
    payload = path.read_bytes()
    rows = [json.loads(line) for line in payload.decode("utf-8").splitlines() if line.strip()] if jsonl else []
    return rows, {"path": str(path.relative_to(root)), "sha256": hashlib.sha256(payload).hexdigest(),
                  "bytes": len(payload), **({"records": len(rows)} if jsonl else {})}


def prepare(root: Path, *, seed: int = 42, output: Path | None = None) -> dict:
    root = root.resolve()
    metadata, sources, metadata_inputs, acquisition_inputs, control_inputs = [], [], [], [], []
    for name in ("global.jsonl", "spain.jsonl"):
        rows, provenance = read_input(root, root / "data/research_225" / name)
        metadata.extend(rows)
        metadata_inputs.append(provenance)
    if len(metadata) != 225:
        raise ValueError("the_research_225_snapshot_must_contain_225_records")
    for path in sorted((root / "data/fulltext").glob("sources_*.jsonl")):
        rows, provenance = read_input(root, path)
        sources.extend(rows)
        acquisition_inputs.append(provenance)
    for relative in ("data/research_225/manifest.json", "data/research_225/PERMISSIONS.json",
                     "data/fulltext/manifest.json", "data/fulltext/PERMISSIONS.json"):
        path = root / relative
        if path.is_file():
            _, provenance = read_input(root, path, jsonl=False)
            control_inputs.append(provenance)
    assignments = make_assignments(metadata, sources, seed)
    target = output.resolve() if output else root / "data/derived/experiments"
    target.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(assignments)
    csv_bytes = buffer.getvalue().encode("utf-8")
    manifest = {
        "schema_version": "0.2.0", "seed": seed,
        "rule": "Union all record_ids sharing any exact PDF SHA-256; group_id=SHA256(sorted members); bucket=int(SHA256('synesis-split-v1\\0'+seed+'\\0'+group_id),16)%10000; train<8000,validation<9000,test otherwise.",
        "target_ratios": {"train": .8, "validation": .1, "test": .1},
        "record_count": len(assignments), "group_count": len({row["group_id"] for row in assignments}),
        "split_record_counts": dict(sorted(Counter(row["split"] for row in assignments).items())),
        "acquisition_records_observed": len(sources), "acquisition_complete": len(sources) == len(metadata),
        "inputs": {"metadata": metadata_inputs, "acquisition_manifests": acquisition_inputs,
                   "control_manifests": control_inputs},
        "output": {"path": "split_assignments.csv", "sha256": hashlib.sha256(csv_bytes).hexdigest(),
                   "bytes": len(csv_bytes)},
        "interpretation": "Approximate group-level 80/10/10 allocation; not stratified or temporal. Every attachment/page/chunk of a work inherits its record group. No AI labels, training, or causal guarantees. Missing PDFs do not imply negative labels. Recompute and freeze after acquisition changes.",
    }
    for name, payload in (("split_assignments.csv", csv_bytes),
                          ("manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode())):
        temporary = target / (name + ".part")
        temporary.write_bytes(payload)
        temporary.replace(target / name)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    manifest = prepare(arguments.root, seed=arguments.seed, output=arguments.output)
    print(json.dumps({key: manifest[key] for key in ("record_count", "group_count", "split_record_counts", "acquisition_complete")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
