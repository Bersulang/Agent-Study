"""Runtime事件契约：停止理由可定位，预算在调用前校验。"""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("runtime_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
class RuntimeTests(unittest.TestCase):
    def test_budget_before_execution(self):
        state = demo.execute(["lookup", "lookup"], budget=1)
        self.assertEqual(state["used"], 1)
        self.assertEqual(state["reason"], "budget")
    def test_cancel_before_execution(self):
        state = demo.execute(["lookup"], cancelled=lambda: True)
        self.assertEqual(state["used"], 0)
        self.assertEqual(state["reason"], "cancelled")
    def test_event_sequence(self):
        state = demo.execute(["lookup"])
        self.assertEqual([event["type"] for event in state["events"]], ["started", "tool_started", "tool_completed", "stopped"])
    def test_unknown_tool(self):
        self.assertEqual(demo.execute(["exec"])["reason"], "unknown_tool")
if __name__ == "__main__":
    unittest.main()
