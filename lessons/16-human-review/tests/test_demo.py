"""审批绑定具体内容；修改、拒绝、过期均不能授权原写入。"""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("review_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.action = {"tool": "create_ticket", "args": {"title": "登录失败"}}
    def test_approved(self):
        approval = demo.make_approval(self.action, decision="approve", now=10)
        self.assertTrue(demo.authorized(self.action, approval, now=11))
    def test_modified_action_invalidates(self):
        approval = demo.make_approval(self.action, decision="approve", now=10)
        changed = {"tool": "create_ticket", "args": {"title": "另一个内容"}}
        self.assertFalse(demo.authorized(changed, approval, now=11))
    def test_denied(self):
        self.assertFalse(demo.authorized(self.action, demo.make_approval(self.action, "reject", 10), 11))
    def test_expired(self):
        self.assertFalse(demo.authorized(self.action, demo.make_approval(self.action, "approve", 10), 71))
if __name__ == "__main__":
    unittest.main()
