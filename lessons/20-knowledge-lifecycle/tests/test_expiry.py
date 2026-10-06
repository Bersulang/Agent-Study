"""过期内容不能继续服务；测试使用显式时间，避免依赖系统时钟。"""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class ExpiryTests(unittest.TestCase):
    def test_expiry_boundary_and_metadata_change(self):
        index = demo.Index()
        index.update("p", "政策", expires=10)
        self.assertIn("p", index.visible(now=9))
        self.assertNotIn("p", index.visible(now=10))
        index.update("p", "政策", expires=20)
        self.assertIn("p", index.visible(now=10))
        self.assertEqual(index.documents["p"]["version"], 2)


if __name__ == "__main__":
    unittest.main()
