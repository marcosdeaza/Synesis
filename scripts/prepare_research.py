"""Prepare metadata features and an unlabelled review queue for all 225 works."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.corpus import load_metadata
from synesis.core import curate, summary


def prepare(root=ROOT):
    metadata, _ = load_metadata(root)
    rows, issues = curate(metadata)
    if issues:
        raise ValueError("metadata_validation_failed")
    reports = root / "reports"
    (reports / "research_features.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    stats = summary(rows)
    stats["scope"] = "All 225 metadata records; title and subjects only; lexical cues do not establish AI use."
    stats["human_labels"] = 0
    (reports / "research_summary.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["record_id", "institution_id", "degree_level", "language", "year", "title", "source_url",
              "annotator_id", "topic_ai", "declared_use_status", "evidence_source", "evidence_location",
              "evidence_note", "date_checked", "rights_reviewed"]
    with (reports / "annotation_queue.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in sorted(metadata, key=lambda row: row["id"]):
            writer.writerow({"record_id": row["id"], **{key: row.get(key) for key in fields[1:7]}})
    return {"metadata_records": len(rows), "human_labels": 0}


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
