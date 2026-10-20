#!/usr/bin/env python3
"""Entry point for the bounded international institutional PDF acquisition."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.acquire_global import main

if __name__ == "__main__":
    main()
