"""阶段13反馈循环迁移参考答案；完成练习并保存证据后再阅读。"""
from pathlib import Path
import importlib.util

example_path = Path(__file__).resolve().parents[1] / "examples" / "feedback_loop.py"
spec = importlib.util.spec_from_file_location("feedback_loop_solution_runtime", example_path)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def solve_feedback(ticket, owners):
    """运行只读工具反馈循环，使用本练习的工单和负责人数据。"""

    def lookup_ticket(ticket_id):
        if ticket_id != ticket["id"]:
            raise ValueError("未知工单")
        return {"ticket_id": ticket["id"], "status": ticket["status"]}

    def lookup_owner(ticket_id):
        if ticket_id not in owners:
            raise ValueError("没有负责人记录")
        return owners[ticket_id]

    def model(history):
        # 模型策略读取最近的工具消息，而不是依赖预先排好的动作列表。
        observations = [message for message in history if message["role"] == "tool"]
        if not observations:
            return runtime.Action("lookup_ticket", {"ticket_id": ticket["id"]})

        latest = observations[-1]
        if not latest["content"]["ok"]:
            return runtime.Action("final", {"text": "资料不足，无法确认工单信息。"})
        if latest["name"] == "lookup_ticket":
            current_ticket = latest["content"]["value"]
            if current_ticket["status"] == "open":
                return runtime.Action("lookup_owner", {"ticket_id": current_ticket["ticket_id"]})
            return runtime.Action("final", {"text": f"工单状态为{current_ticket['status']}。"})
        return runtime.Action("final", {"text": f"工单负责人为{latest['content']['value']}。"})

    return runtime.run_agent(model, {
        "lookup_ticket": lookup_ticket,
        "lookup_owner": lookup_owner,
    })


if __name__ == "__main__":
    cases = [
        ({"id": "T-1", "status": "open"}, {"T-1": "Lin"}),
        ({"id": "T-2", "status": "closed"}, {"T-2": "Chen"}),
    ]
    for ticket, owners in cases:
        result = solve_feedback(ticket, owners)
        print(result.reason, result.answer, [step["name"] for step in result.trace])
