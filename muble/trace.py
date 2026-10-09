"""Versioned MuJoCo-body pose traces consumed by Blender 4.5."""

from __future__ import annotations

import math
from typing import Iterable, Mapping


BODY_POSE_TRACE_SCHEMA = "muble/body-pose-trace-v1"


def _finite_vector(value, length: int, field: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != length:
        raise ValueError(f"{field} must contain {length} values")
    result = [float(item) for item in value]
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{field} must be finite")
    return result


def body_pose_frame(
    frame_index: int,
    simulation_time: float,
    poses: Mapping[str, Mapping[str, Iterable[float]]],
) -> dict:
    if isinstance(frame_index, bool) or not isinstance(frame_index, int) or frame_index < 0:
        raise ValueError("frame_index must be a non-negative integer")
    simulation_time = float(simulation_time)
    if not math.isfinite(simulation_time) or simulation_time < 0:
        raise ValueError("simulation_time must be finite and non-negative")
    checked = {}
    for name, pose in poses.items():
        if not isinstance(name, str) or not name:
            raise ValueError("body names must be non-empty strings")
        checked[name] = {
            "position": _finite_vector(pose.get("position"), 3, f"{name}.position"),
            "quaternion_wxyz": _finite_vector(
                pose.get("quaternion_wxyz"), 4, f"{name}.quaternion_wxyz"
            ),
        }
    return {
        "frame_index": frame_index,
        "simulation_time": simulation_time,
        "bodies": checked,
    }


def validate_body_pose_trace(trace: object) -> dict:
    if not isinstance(trace, dict):
        raise ValueError("trace must be an object")
    if trace.get("schema") != BODY_POSE_TRACE_SCHEMA:
        raise ValueError(f"trace schema must be {BODY_POSE_TRACE_SCHEMA}")
    frames = trace.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("trace frames must be a non-empty list")
    checked = [
        body_pose_frame(
            frame["frame_index"], frame["simulation_time"], frame["bodies"]
        )
        for frame in frames
    ]
    if [frame["frame_index"] for frame in checked] != list(range(len(checked))):
        raise ValueError("trace frame indices must be contiguous from zero")
    body_names = set(checked[0]["bodies"])
    if any(set(frame["bodies"]) != body_names for frame in checked[1:]):
        raise ValueError("every frame must contain the same body names")
    return {**trace, "frames": checked}
