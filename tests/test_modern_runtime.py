import unittest

try:
    import mujoco  # noqa: F401
except ImportError:
    mujoco = None

from muble.trace import BODY_POSE_TRACE_SCHEMA, validate_body_pose_trace


@unittest.skipIf(mujoco is None, "modern MuJoCo dependency is not installed")
class MujocoRuntimeTest(unittest.TestCase):
    def test_named_joint_and_body_pose_roundtrip(self):
        from muble.runtime import MujocoRuntime

        runtime = MujocoRuntime.from_xml_string(
            """
            <mujoco>
              <worldbody>
                <body name="root">
                  <body name="moving">
                    <joint name="hinge" type="hinge" axis="0 0 1"/>
                    <geom type="box" size=".01 .01 .01" pos=".1 0 0"/>
                  </body>
                </body>
              </worldbody>
            </mujoco>
            """
        )
        runtime.set_joint_positions({"hinge": 0.25})
        self.assertAlmostEqual(runtime.joint_positions(("hinge",))["hinge"], 0.25)
        pose = runtime.body_poses(("moving",))["moving"]
        self.assertEqual(len(pose["position"]), 3)
        self.assertEqual(len(pose["quaternion_wxyz"]), 4)


class BodyPoseTraceTest(unittest.TestCase):
    def test_trace_requires_contiguous_frames_and_stable_body_names(self):
        trace = {
            "schema": BODY_POSE_TRACE_SCHEMA,
            "frames": [
                {
                    "frame_index": 0,
                    "simulation_time": 0.0,
                    "bodies": {
                        "object": {
                            "position": [0, 0, 0],
                            "quaternion_wxyz": [1, 0, 0, 0],
                        }
                    },
                }
            ],
        }
        checked = validate_body_pose_trace(trace)
        self.assertEqual(checked["frames"][0]["bodies"]["object"]["position"], [0.0, 0.0, 0.0])

        broken = {**trace, "frames": [{**trace["frames"][0], "frame_index": 1}]}
        with self.assertRaisesRegex(ValueError, "contiguous"):
            validate_body_pose_trace(broken)



if __name__ == "__main__":
    unittest.main()
