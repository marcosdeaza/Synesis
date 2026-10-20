"""Validate the complete 225-record acquisition ledger, optionally checking assets."""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.fulltext import validate_fulltext

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-files", action="store_true")
    parser.add_argument("--allow-incomplete", action="store_true", help="During acquisition only")
    args = parser.parse_args()
    result = validate_fulltext(args.root, require_files=args.require_files, require_complete=not args.allow_incomplete)
    reports = args.root / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "fulltext_coverage.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["institution_id", "metadata_records", "attempted_records", "downloaded_records", "pdf_files", "pdf_bytes"]
    with (reports / "fulltext_coverage.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["institutions"])
    print(json.dumps({key: result[key] for key in ("metadata_records", "attempted_records", "downloaded_records", "pdf_files", "pdf_bytes", "statuses")}, ensure_ascii=False, indent=2))
