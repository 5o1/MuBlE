#!/usr/bin/env python3
"""Construct, reset, and step the modern robosuite TabletopEnv."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from environment.tabletop_env import TabletopEnv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=100)
    args = parser.parse_args()
    if args.steps <= 0:
        raise ValueError("steps must be positive")

    env = TabletopEnv(
        objs={},
        robots="Panda",
        gripper_types="Robotiq85Gripper",
        has_renderer=False,
        has_offscreen_renderer=False,
        use_camera_obs=False,
        use_object_obs=False,
        ignore_done=True,
        debug=False,
        blender_render=False,
        use_custom_controller=False,
    )
    try:
        observation = env.reset()
        action = np.zeros(env.action_dim)
        action[-1] = -1
        for _ in range(args.steps):
            observation, reward, done, _ = env.step(action)
        report = {
            "schema_version": 1,
            "steps": args.steps,
            "action_dim": env.action_dim,
            "observation_keys": sorted(observation),
            "nq": int(env.sim.model.nq),
            "nv": int(env.sim.model.nv),
            "simulation_time": float(env.sim.data.time),
            "finite_qpos": bool(np.isfinite(env.sim.data.qpos).all()),
            "eef_position": observation["robot0_eef_pos"].tolist(),
            "reward": float(reward),
            "done": bool(done),
        }
    finally:
        env.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
