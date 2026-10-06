"""扩展需求回归：真实状态、失败边界和副作用保持。"""
import runpy
import unittest
from pathlib import Path

class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))
    def test_span_keeps_error_type_without_secret(self):
        events = []
        with self.assertRaises(TimeoutError):
            with self.api["span"](events, "request-x", "tool"):
                raise TimeoutError("sensitive-secret")
        self.assertEqual(events[0].get("error_type"), "TimeoutError")
        self.assertNotIn("sensitive-secret", str(events))

if __name__ == "__main__":
    unittest.main()
