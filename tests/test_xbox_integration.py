import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / "integrations" / "xbox_gamepad" / "blender_binding.json"
TRACE = ROOT / "results" / "xbox_gamepad_probe" / "probe_trace.json"


class XboxBindingTest(unittest.TestCase):
    def test_binding_covers_sixteen_unique_parts_objects_and_bodies(self):
        binding = json.loads(BINDING.read_text())
        parts = binding["parts"]
        self.assertEqual(len(parts), 16)
        self.assertEqual(len({record["blender_object"] for record in parts.values()}), 16)
        self.assertIn("controller_body", {record["body"] for record in parts.values()})
        self.assertEqual(binding["source_to_simulation_rotation"], "positive_90_degrees_about_x")

    def test_recorded_probe_moves_only_the_commanded_control_body(self):
        trace = json.loads(TRACE.read_text())
        self.assertEqual(trace["schema"], "muble/body-pose-trace-v1")
        self.assertEqual([item["label"] for item in trace["controls"]], [
            "neutral", "a_pressed", "left_stick_x_positive"
        ])
        neutral, a_pressed, stick = trace["frames"]

        self.assertNotEqual(neutral["bodies"]["a"], a_pressed["bodies"]["a"])
        self.assertEqual(neutral["bodies"]["b"], a_pressed["bodies"]["b"])
        self.assertNotEqual(
            neutral["bodies"]["left_stick"], stick["bodies"]["left_stick"]
        )
        self.assertEqual(
            neutral["bodies"]["right_stick"], stick["bodies"]["right_stick"]
        )


if __name__ == "__main__":
    unittest.main()
