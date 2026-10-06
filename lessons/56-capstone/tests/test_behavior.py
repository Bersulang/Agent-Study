"""课程行为回归测试：验证真实函数的成功与失败路径。"""
import runpy
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parents[1] / 'examples' / 'demo.py'

class BehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 加载教学实现，不执行其中的命令行演示入口。
        cls.api = runpy.run_path(str(CODE))
    def setUp(self):
        from tempfile import TemporaryDirectory
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / "test.db"
        self.assistant = self.api["Assistant"](self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_restart_replay_no_duplicate(self):
        pending = self.assistant.request("lab-a", "创建工单:问题", "k1")
        first = self.assistant.approve("lab-a", "k1", pending["digest"])
        restored = self.api["Assistant"](self.path)
        self.assertEqual(restored.approve("lab-a", "k1", pending["digest"]), first)
        self.assertEqual(restored.request("lab-a", "查询政策", "q1")["ticket_count"], 1)

    def test_cross_tenant_approval_denied(self):
        pending = self.assistant.request("lab-a", "创建工单:问题", "k1")
        with self.assertRaises(PermissionError):
            self.assistant.approve("lab-b", "k1", pending["digest"])

    def test_key_conflict_denied(self):
        self.assistant.request("lab-a", "创建工单:原始问题", "k1")
        with self.assertRaises(ValueError):
            self.assistant.request("lab-a", "创建工单:不同问题", "k1")

    def test_cancel_blocks_write(self):
        pending = self.assistant.request("lab-a", "创建工单:问题", "k1")
        self.assistant.cancel("lab-a", "k1")
        with self.assertRaises(PermissionError):
            self.assistant.approve("lab-a", "k1", pending["digest"])

    def test_expired_approval_denied(self):
        pending = self.assistant.request("lab-a", "创建工单:问题", "k1", now=0)
        with self.assertRaises(PermissionError):
            self.assistant.approve("lab-a", "k1", pending["digest"], now=60)

    def test_changed_digest_denied(self):
        self.assistant.request("lab-a", "创建工单:问题", "k1")
        with self.assertRaises(PermissionError):
            self.assistant.approve("lab-a", "k1", "changed")

    def test_reader_cannot_draft(self):
        with self.assertRaises(PermissionError):
            self.assistant.request("lab-reader", "创建工单:问题", "k1")

    def test_unknown_model_action_denied(self):
        assistant = self.api["Assistant"](self.path, planner=lambda text: {"action": "shell"})
        with self.assertRaises(PermissionError):
            assistant.request("lab-a", "whatever", "k1")

    def test_revision_invalidates_old_approval(self):
        pending = self.assistant.request("lab-a", "创建工单:原问题", "k1")
        revised = self.assistant.revise("lab-a", "k1", "新问题", now=10)
        self.assertNotEqual(revised["digest"], pending["digest"])
        with self.assertRaises(PermissionError):
            self.assistant.approve("lab-a", "k1", pending["digest"], now=11)
        self.assertEqual(self.assistant.approve("lab-a", "k1", revised["digest"], now=11)["status"], "done")

    def test_read_tool_is_tenant_scoped(self):
        pending = self.assistant.request("lab-a", "创建工单:私有问题", "k1")
        self.assistant.approve("lab-a", "k1", pending["digest"])
        self.assertEqual(self.assistant.ticket_summary("lab-a", "k1")["title"], "私有问题")
        self.assertIsNone(self.assistant.ticket_summary("lab-b", "k1"))

    def test_model_plan_schema_rejects_unknown_action(self):
        planner_api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "solutions/model_planner.py"))
        class FakeClient:
            def complete(self, messages):
                return {"text": '{"action":"shell","command":"anything"}'}
        with self.assertRaises(ValueError):
            planner_api["ModelPlanner"](FakeClient())("task")

    def test_new_knowledge_still_scoped(self):
        extension = runpy.run_path(str(Path(__file__).resolve().parents[1] / "solutions/knowledge_extension.py"))
        assistant = extension["ExtendedAssistant"](self.path)
        self.assertEqual(assistant.request("lab-a", "如何登录", "q1")["evidence"]["source"], "fixture-login-v1")
        self.assertEqual(assistant.request("lab-b", "如何登录", "q1")["status"], "no_evidence")

if __name__ == "__main__":
    unittest.main()
