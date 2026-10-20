#!/usr/bin/env python3
"""Build the local full-text corpus without modifying metadata snapshots or PDFs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.corpus import build_corpus  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Construir catálogo, páginas, chunks y SQLite de Synesis.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="Directorio derivado; por defecto data/derived.")
    parser.add_argument("--max-chars", type=int, default=1800)
    parser.add_argument("--overlap", type=int, default=200)
    args = parser.parse_args()
    try:
        summary = build_corpus(args.root, args.output, max_chars=args.max_chars, overlap=args.overlap)
        reports = args.root / "reports"
        reports.mkdir(parents=True, exist_ok=True)
        report = reports / "corpus_summary.json"
        report.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError):
        print("corpus_build_failed: revisar entradas, configuración y permisos locales; no se muestran contenidos en los logs.", file=sys.stderr)
        return 1
    print(json.dumps({key: summary[key] for key in ("metadata_records", "records_with_verified_pdf", "records_with_text", "page_count", "chunk_count", "fts5_available", "issue_counts")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
