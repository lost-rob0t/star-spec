#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: check_official_manifest.py OFFICIAL GENERATED")
    official = json.loads(Path(sys.argv[1]).read_text())
    generated = json.loads(Path(sys.argv[2]).read_text())
    if official != generated:
        raise SystemExit("checked-in portable manifest differs from the official StarLang compiler")


if __name__ == "__main__":
    main()
