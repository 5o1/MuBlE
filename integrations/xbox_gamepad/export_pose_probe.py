#!/usr/bin/env python3
"""Export three Xbox MJCF body-pose probes for the MuBlE Blender bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from muble import BODY_POSE_TRACE_SCHEMA, MujocoRuntime, body_pose_frame


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xbox-package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    package = args.xbox_package.resolve(strict=True)
    profile = package / "resource_data" / "mujoco" / "full_controls_estimated_v0"
    robotwin = package / "resource_data" / "robotwin" / "full_controls_estimated_v0"
    manifest = load(profile / "manifest.json")
    visual_binding = load(robotwin / "visual" / "manifest.json")
    runtime = MujocoRuntime.from_xml_path(profile / manifest["entrypoint"])

    part_to_body = {
        part: visual_binding["root_link"] for part in visual_binding["static_parts"]
    }
    part_to_body.update(
        {
            part: record["link"]
            for part, record in visual_binding["moving_parts"].items()
        }
    )
    bodies = tuple(dict.fromkeys(part_to_body.values()))
    joints = tuple(manifest["bindings"]["joints"])
    limits = {
        item["joint"]: (float(item["lower"]), float(item["upper"]))
        for field in ("axes", "scalars", "splits", "physical_events")
        for item in manifest["state_mapping"].get(field, [])
    }
    probes = (
        ("neutral", {}),
        ("a_pressed", {"a_press": limits["a_press"][1]}),
        ("left_stick_x_positive", {"left_stick_x": limits["left_stick_x"][1]}),
    )
    frames = []
    controls = []
    for index, (label, position) in enumerate(probes):
        runtime.set_joint_positions({name: 0.0 for name in joints})
        runtime.set_joint_positions(position)
        frames.append(
            body_pose_frame(
                index,
                index * runtime.timestep,
                runtime.body_poses(bodies),
            )
        )
        controls.append({"frame_index": index, "label": label, "qpos": position})

    trace = {
        "schema": BODY_POSE_TRACE_SCHEMA,
        "generator": "integrations/xbox_gamepad/export_pose_probe.py",
        "asset": "Xbox One S",
        "profile": "full_controls_estimated_v0",
        "source_mjcf": str((profile / manifest["entrypoint"]).resolve()),
        "part_to_body": part_to_body,
        "controls": controls,
        "frames": frames,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"frames": len(frames), "bodies": len(bodies), "output": str(args.output)}))


if __name__ == "__main__":
    main()
