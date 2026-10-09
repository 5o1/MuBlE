"""Modern MuBlE runtime interfaces with a lazy MuJoCo import."""

from .trace import BODY_POSE_TRACE_SCHEMA, body_pose_frame, validate_body_pose_trace

__all__ = [
    "BODY_POSE_TRACE_SCHEMA",
    "MujocoRuntime",
    "body_pose_frame",
    "validate_body_pose_trace",
]


def __getattr__(name):
    if name == "MujocoRuntime":
        from .runtime import MujocoRuntime

        return MujocoRuntime
    raise AttributeError(name)
