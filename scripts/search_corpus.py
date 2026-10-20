#!/usr/bin/env python3
"""Search the local corpus read-only; emit cited excerpts as JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.corpus import search_corpus  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Buscar texto en el corpus local de Synesis.")
    parser.add_argument("query")
    parser.add_argument("--database", type=Path, default=ROOT / "data/derived/corpus.sqlite")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--institution")
    parser.add_argument("--degree", choices=("bachelor", "master", "unknown"))
    parser.add_argument("--year-min", type=int)
    parser.add_argument("--year-max", type=int)
    parser.add_argument("--literal", action="store_true", help="Tratar consulta como frase literal, sin operadores FTS.")
    args = parser.parse_args()
    try:
        result = search_corpus(args.database, args.query, args.limit, institution=args.institution,
                               degree=args.degree, year_min=args.year_min, year_max=args.year_max,
                               literal=args.literal)
    except (ValueError, OSError):
        print("corpus_search_failed: comprobar base, límite y sintaxis; usar --literal para una frase.", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
