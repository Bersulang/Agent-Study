"""扩展需求回归：真实状态、失败边界和副作用保持。"""
import runpy
import unittest
from pathlib import Path

class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))
    def test_category_floor_cannot_be_hidden_by_average(self):
        report = {"success_rate": .95, "security_violations": [], "by_category": {"normal": 1, "incomplete": 0}}
        self.assertIn("release_decision", self.api, "扩展功能尚未实现")
        self.assertFalse(self.api["release_decision"](report))

if __name__ == "__main__":
    unittest.main()
