# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        self.assertEqual(demo.search("薪资", "ENG"), [])
        self.assertIn("hr", demo.search("薪资", "HR"))
        with self.assertRaises(PermissionError):
            demo.search("薪资", "ADMIN")
        self.assertTrue(demo.detect_conflict([{"value": 1}, {"value": 2}]))

if __name__ == "__main__":
    unittest.main()
