# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        result = demo.research(["发票", "审批", "期限"], 2)
        self.assertEqual(len(result["trace"]), 2)
        self.assertEqual(result["missing"], ["期限"])
        self.assertEqual(demo.research(["发票"], 0)["status"], "partial")
        self.assertEqual(len(demo.research(["发票", "发票"])["trace"]), 1)

if __name__ == "__main__":
    unittest.main()
