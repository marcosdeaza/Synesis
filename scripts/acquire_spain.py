#!/usr/bin/env python3
"""Run the resumable Spanish PDF acquisition from any working directory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from synesis.acquire_spain import main

if __name__ == "__main__":
    main()
