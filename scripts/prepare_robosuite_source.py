#!/usr/bin/env python3
"""Apply MuJoCo 3.15 compatibility to a pinned robosuite 1.5.2 checkout."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


EXPECTED_COMMIT = "824ac14cefcfb7ec125fe5eb2e0bad7364466154"
ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "robosuite-1.5.2-mujoco-3.15.patch"


def run(source: Path, *args: str, check: bool = True):
    return subprocess.run(
        ["git", "-C", str(source), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    commit = run(source, "rev-parse", "HEAD").stdout.strip()
    if commit != EXPECTED_COMMIT:
        raise SystemExit(
            f"robosuite source must be {EXPECTED_COMMIT}, got {commit}"
        )
    patch = str(PATCH.resolve(strict=True))
    clean = run(source, "apply", "--check", patch, check=False)
    if clean.returncode == 0:
        run(source, "apply", patch)
        print(f"applied {PATCH.name} to {commit}")
        return
    reverse = run(source, "apply", "--reverse", "--check", patch, check=False)
    if reverse.returncode == 0:
        print(f"already applied {PATCH.name} to {commit}")
        return
    raise SystemExit(clean.stderr.strip() or "robosuite patch cannot be applied")


if __name__ == "__main__":
    main()
