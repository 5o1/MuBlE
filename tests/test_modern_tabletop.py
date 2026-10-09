import unittest
import inspect


try:
    import mujoco  # noqa: F401
    import robosuite  # noqa: F401
except ImportError:
    robosuite = None


@unittest.skipIf(robosuite is None, "modern robosuite dependencies are not installed")
class ModernTabletopImportTest(unittest.TestCase):
    def test_tabletop_targets_manipulation_env_and_builtin_controller(self):
        from environment.tabletop_env import TabletopEnv
        from robosuite.environments.manipulation.manipulation_env import ManipulationEnv

        self.assertTrue(issubclass(TabletopEnv, ManipulationEnv))
        parameter = inspect.signature(TabletopEnv.__init__).parameters[
            "use_custom_controller"
        ]
        self.assertFalse(parameter.default)


if __name__ == "__main__":
    unittest.main()
