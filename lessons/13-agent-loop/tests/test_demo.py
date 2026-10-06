"""脚本模型只测试控制流；覆盖停止、未知工具和连续失败。"""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("loop_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
class LoopTests(unittest.TestCase):
    def test_final(self):
        result = demo.run([{ "type": "tool", "name": "lookup", "args": {"id": "T1"}}, {"type": "final", "text": "已找到"}])
        self.assertEqual(result["reason"], "completed")
        self.assertEqual(len(result["observations"]), 1)
    def test_step_budget(self):
        result = demo.run([{"type": "tool", "name": "lookup", "args": {"id": "T1"}}] * 5, max_steps=2)
        self.assertEqual(result["reason"], "step_budget")
    def test_unknown_tool_stops_after_two_failures(self):
        result = demo.run([{"type": "tool", "name": "exec", "args": {}}] * 4)
        self.assertEqual(result["reason"], "consecutive_failures")
if __name__ == "__main__":
    unittest.main()
