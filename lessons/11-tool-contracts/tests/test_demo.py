"""工具先验证输入，再返回稳定信封；未知工具不得动态执行。"""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("tool_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
class ToolTests(unittest.TestCase):
    def test_success(self):
        self.assertEqual(demo.dispatch("ticket_lookup", {"id": "T1"})["data"]["status"], "open")
    def test_invalid_arguments(self):
        self.assertEqual(demo.dispatch("ticket_lookup", {"id": 1})["error"]["code"], "invalid_arguments")
    def test_unknown_tool(self):
        self.assertEqual(demo.dispatch("exec", {})["error"]["code"], "unknown_tool")
    def test_missing_ticket(self):
        self.assertEqual(demo.dispatch("ticket_lookup", {"id": "T99"})["error"]["code"], "not_found")
if __name__ == "__main__":
    unittest.main()
