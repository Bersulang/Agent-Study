# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        original = {"stage": "draft"}
        waiting = demo.step(original)
        self.assertEqual(original["stage"], "draft")
        self.assertEqual(demo.step(waiting)["stage"], "waiting")
        self.assertEqual(demo.step(waiting, False)["stage"], "rejected")
        with self.assertRaises(ValueError):
            demo.step(waiting, "yes")

if __name__ == "__main__":
    unittest.main()
