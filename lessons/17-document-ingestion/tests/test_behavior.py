# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        self.assertEqual(demo.ingest("甲乙丙丁", "a.md", 2)[1]["offset"], 2)
        self.assertEqual(demo.ingest("甲\n\n乙", "a.md")[1]["paragraph"], 2)
        with self.assertRaises(ValueError):
            demo.ingest("  ", "empty.pdf")

if __name__ == "__main__":
    unittest.main()
