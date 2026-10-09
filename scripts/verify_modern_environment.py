#!/usr/bin/env python3
"""Fail closed unless the modern MuBlE runtime versions are active."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", type=Path, required=True)
    parser.add_argument("--base-scene", type=Path, required=True)
    args = parser.parse_args()

    import cv2
    import mujoco
    import numpy
    import robosuite

    blender = args.blender.resolve(strict=True)
    base_scene = args.base_scene.resolve(strict=True)
    version = subprocess.run(
        [str(blender), "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()[0]
    report = {
        "python": sys.version.split()[0],
        "mujoco": mujoco.__version__,
        "robosuite": robosuite.__version__,
        "numpy": numpy.__version__,
        "opencv": cv2.__version__,
        "blender": version,
        "base_scene": str(base_scene),
    }
    expected = {
        "python": "3.12",
        "mujoco": "3.15.",
        "robosuite": "1.5.2",
        "numpy": "1.26.4",
        "opencv": "4.10.0",
        "blender": "Blender 4.5.",
    }
    failures = [
        f"{name}: expected prefix {prefix!r}, got {report[name]!r}"
        for name, prefix in expected.items()
        if not report[name].startswith(prefix)
    ]
    if failures:
        raise SystemExit("; ".join(failures))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
