"""反馈循环必须把工具观测交回模型，并保护控制边界。"""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "examples" / "feedback_loop.py"
spec = importlib.util.spec_from_file_location("feedback_loop", path)
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class FeedbackLoopTests(unittest.TestCase):
    @staticmethod
    def reject_tool_input():
        """用可读函数显式表示工具业务拒绝。"""
        raise ValueError("fixture detail must not leak")

    def test_tool_observation_changes_the_next_model_action(self):
        calls = []

        def model(history):
            calls.append([message.copy() for message in history])
            observations = [m["content"] for m in history if m["role"] == "tool"]
            if not observations:
                return loop.Action("lookup", {"ticket_id": "T1"})
            if observations[-1]["ok"]:
                return loop.Action("final", {"text": observations[-1]["value"]["status"]})
            return loop.Action("retry_help", {"ticket_id": "T1"})

        tools = {
            "lookup": lambda ticket_id: {"status": "open", "ticket_id": ticket_id},
            "retry_help": lambda ticket_id: f"需要人工检查 {ticket_id}",
        }
        result = loop.run_agent(model, tools, max_steps=4)

        self.assertEqual(result.reason, "completed")
        self.assertEqual(result.answer, "open")
        self.assertEqual(len(calls), 2)
        self.assertIn("role", calls[1][-1])
        self.assertEqual(calls[1][-1]["role"], "tool")

    def test_tool_result_changes_the_follow_up_action(self):
        for status, expected_tool in [("open", "notify"), ("closed", "archive")]:
            executed = []

            def model(history):
                tool_messages = [m for m in history if m["role"] == "tool"]
                if not tool_messages:
                    return loop.Action("lookup", {})
                if len(tool_messages) == 1:
                    next_action = "notify" if tool_messages[-1]["content"]["value"]["status"] == "open" else "archive"
                    return loop.Action(next_action, {})
                return loop.Action("final", {"text": tool_messages[-1]["content"]["value"]})

            result = loop.run_agent(model, {
                "lookup": lambda: {"status": status},
                "notify": lambda: executed.append("notify") or "notified",
                "archive": lambda: executed.append("archive") or "archived",
            }, max_steps=4)
            self.assertEqual(executed, [expected_tool])
            self.assertEqual(result.answer, "notified" if expected_tool == "notify" else "archived")

    def test_demo_model_runs_open_and_closed_paths(self):
        for status, expected_names in [
            ("open", ["lookup_ticket", "lookup_owner"]),
            ("closed", ["lookup_ticket"]),
        ]:
            result = loop.run_agent(loop.demo_model, {
                "lookup_ticket": lambda ticket_id: {"ticket_id": ticket_id, "status": status},
                "lookup_owner": lambda ticket_id: "Lin",
            })
            tool_names = [step["name"] for step in result.trace]
            self.assertEqual(result.reason, "completed")
            self.assertEqual(tool_names, expected_names)

    def test_step_budget_stops_before_extra_tool_calls(self):
        executed = []
        result = loop.run_agent(
            lambda history: loop.Action("write", {}),
            {"write": lambda: executed.append("called")},
            max_steps=2,
        )
        self.assertEqual(result.reason, "step_budget")
        self.assertEqual(executed, ["called", "called"])

    def test_unknown_tools_and_repeated_failures_stop_safely(self):
        result = loop.run_agent(
            lambda history: loop.Action("missing", {}), {},
            max_steps=5, max_consecutive_failures=2,
        )
        self.assertEqual(result.reason, "consecutive_failures")
        self.assertEqual(len(result.trace), 2)
        self.assertTrue(all(not step["ok"] for step in result.trace))

    def test_invalid_action_and_tool_exception_become_observations(self):
        actions = iter([{"type": "unsafe"}, loop.Action("break", {})])
        result = loop.run_agent(
            lambda history: next(actions), {"break": self.reject_tool_input},
            max_steps=4, max_consecutive_failures=2,
        )
        self.assertEqual(result.reason, "consecutive_failures")
        self.assertEqual(len(result.trace), 2)
        self.assertEqual(result.trace[-1]["error"], "工具拒绝了输入，请检查参数")

    def test_programming_errors_are_not_hidden(self):
        with self.assertRaises(ZeroDivisionError):
            loop.run_agent(lambda history: loop.Action("bug", {}), {"bug": lambda: 1 / 0})

    def test_boolean_is_not_an_integer_budget(self):
        with self.assertRaises(ValueError):
            loop.run_agent(lambda history: loop.Action("final", {"text": "done"}), {}, max_steps=True)

    def test_final_action_terminates_without_running_tools(self):
        executed = []
        result = loop.run_agent(
            lambda history: loop.Action("final", {"text": "完成"}),
            {"write": lambda: executed.append(True)},
        )
        self.assertEqual(result.reason, "completed")
        self.assertEqual(result.answer, "完成")
        self.assertEqual(executed, [])


if __name__ == "__main__":
    unittest.main()
