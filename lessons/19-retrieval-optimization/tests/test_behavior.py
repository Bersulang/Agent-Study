# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        self.assertEqual(demo.search("差旅 凭证")[0], "A")
        self.assertNotIn("C", demo.search("报销 发票"))
        self.assertEqual(demo.metrics(["A", "B"], ["A"])["recall"], 0.5)

if __name__ == "__main__":
    unittest.main()
