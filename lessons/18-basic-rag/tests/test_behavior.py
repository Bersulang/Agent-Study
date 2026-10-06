# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        self.assertEqual(demo.answer("工资")["citations"], [])
        self.assertEqual(demo.answer("报销")["citations"], ["policy.md#1"])
        self.assertEqual(demo.retrieve(""), [])

if __name__ == "__main__":
    unittest.main()
