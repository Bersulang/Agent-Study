"""有依赖的工作流不得提前写入，路由结果均有终止状态。"""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("workflow_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
class WorkflowTests(unittest.TestCase):
    def test_known_route(self):
        self.assertEqual(demo.workflow("登录", evidence=True)["state"], "answered")
    def test_missing_evidence_replans_once(self):
        result = demo.workflow("登录", evidence=False)
        self.assertEqual(result["state"], "human_review")
        self.assertEqual(result["replans"], 1)
    def test_unknown_route_clarifies(self):
        self.assertEqual(demo.workflow("其他", evidence=True)["state"], "clarify")
    def test_replan_budget(self):
        self.assertEqual(demo.workflow("登录", evidence=False, max_replans=0)["state"], "stopped")
if __name__ == "__main__":
    unittest.main()
