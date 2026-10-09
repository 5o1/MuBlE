"""Small official-MuJoCo runtime used by modern MuBlE integrations."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import mujoco
import numpy as np


class MujocoRuntime:
    """Name-addressed facade over ``mujoco.MjModel`` and ``MjData``."""

    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData | None = None):
        if not isinstance(model, mujoco.MjModel):
            raise TypeError("model must be mujoco.MjModel")
        self.model = model
        self.data = data if data is not None else mujoco.MjData(model)
        if not isinstance(self.data, mujoco.MjData):
            raise TypeError("data must be mujoco.MjData")
        mujoco.mj_forward(self.model, self.data)

    @classmethod
    def from_xml_path(cls, path: str | Path) -> "MujocoRuntime":
        path = Path(path).resolve(strict=True)
        return cls(mujoco.MjModel.from_xml_path(str(path)))

    @classmethod
    def from_xml_string(cls, xml: str) -> "MujocoRuntime":
        if not isinstance(xml, str) or not xml.strip():
            raise ValueError("xml must be a non-empty string")
        return cls(mujoco.MjModel.from_xml_string(xml))

    @property
    def timestep(self) -> float:
        return float(self.model.opt.timestep)

    def reset(self) -> None:
        mujoco.mj_resetData(self.model, self.data)
        mujoco.mj_forward(self.model, self.data)

    def forward(self) -> None:
        mujoco.mj_forward(self.model, self.data)

    def step(self, count: int = 1) -> None:
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError("count must be a positive integer")
        for _ in range(count):
            mujoco.mj_step(self.model, self.data)

    def joint_positions(self, names: Iterable[str]) -> dict[str, float]:
        values = {}
        for name in names:
            joint_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, str(name)
            )
            if joint_id < 0:
                raise KeyError(f"unknown MuJoCo joint {name!r}")
            joint_type = int(self.model.jnt_type[joint_id])
            if joint_type not in (
                int(mujoco.mjtJoint.mjJNT_HINGE),
                int(mujoco.mjtJoint.mjJNT_SLIDE),
            ):
                raise ValueError(f"joint {name!r} is not scalar")
            values[str(name)] = float(self.data.qpos[self.model.jnt_qposadr[joint_id]])
        return values

    def set_joint_positions(self, positions: Mapping[str, float]) -> None:
        for name, raw in positions.items():
            value = float(raw)
            if not np.isfinite(value):
                raise ValueError(f"joint position {name!r} must be finite")
            joint_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, str(name)
            )
            if joint_id < 0:
                raise KeyError(f"unknown MuJoCo joint {name!r}")
            joint_type = int(self.model.jnt_type[joint_id])
            if joint_type not in (
                int(mujoco.mjtJoint.mjJNT_HINGE),
                int(mujoco.mjtJoint.mjJNT_SLIDE),
            ):
                raise ValueError(f"joint {name!r} is not scalar")
            self.data.qpos[self.model.jnt_qposadr[joint_id]] = value
        mujoco.mj_forward(self.model, self.data)

    def body_poses(self, names: Iterable[str]) -> dict[str, dict[str, list[float]]]:
        poses = {}
        for name in names:
            body_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_BODY, str(name)
            )
            if body_id < 0:
                raise KeyError(f"unknown MuJoCo body {name!r}")
            poses[str(name)] = {
                "position": [float(value) for value in self.data.xpos[body_id]],
                "quaternion_wxyz": [
                    float(value) for value in self.data.xquat[body_id]
                ],
            }
        return poses
