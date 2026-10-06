"""扩展需求回归：真实状态、失败边界和副作用保持。"""
import runpy
import unittest
from pathlib import Path

class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))
    def test_writer_without_bound_approval_has_no_effect(self):
        self.assertIn("write_ticket", self.api, "扩展功能尚未实现")
        tickets, audit = {("A", "T-001"): "open"}, []
        with self.assertRaises(PermissionError):
            self.api["write_ticket"]("session-a", "A", "T-001", "done", None, tickets, audit)
        self.assertEqual(tickets[("A", "T-001")], "open")

    def test_approval_cannot_grant_writer_role(self):
        self.assertIn("write_ticket", self.api, "扩展功能尚未实现")
        tickets, audit = {("B", "T-001"): "open"}, []
        approval = {"tenant": "B", "ticket_id": "T-001", "state": "done"}
        with self.assertRaises(PermissionError):
            self.api["write_ticket"]("session-b", "B", "T-001", "done", approval, tickets, audit)
        self.assertEqual(tickets[("B", "T-001")], "open")

    def test_writer_with_matching_approval_updates_only_owned_ticket(self):
        self.assertIn("write_ticket", self.api, "扩展功能尚未实现")
        tickets, audit = {("A", "T-001"): "open", ("B", "T-001"): "open"}, []
        approval = {"tenant": "A", "ticket_id": "T-001", "state": "done"}
        self.api["write_ticket"]("session-a", "A", "T-001", "done", approval, tickets, audit)
        self.assertEqual(tickets, {("A", "T-001"): "done", ("B", "T-001"): "open"})
        self.assertTrue(audit[-1]["allowed"])

if __name__ == "__main__":
    unittest.main()
