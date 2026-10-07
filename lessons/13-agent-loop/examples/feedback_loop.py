"""用可替换的模拟模型演示模型—工具—观测反馈控制闭环。"""


class Action:
    """模型一次决策的结构：工具名和参数，或一条最终回答。"""

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class RunResult:
    """保存运行结束时可检查的回答、原因、消息历史和工具轨迹。"""

    def __init__(self, answer, reason, history, trace):
        self.answer = answer
        self.reason = reason
        self.history = history
        self.trace = trace


def run_agent(model, tools, max_steps=5, max_consecutive_failures=2):
    """执行有限反馈循环；model(history)是注入的决策函数。"""
    if type(max_steps) is not int or type(max_consecutive_failures) is not int:
        raise ValueError("步数预算和连续失败上限必须是整数")
    if max_steps < 1 or max_consecutive_failures < 1:
        raise ValueError("步数预算和连续失败上限必须至少为1")

    # role标明消息来源；tool内容保留本轮工具名、调用编号、成功标志和结果。
    history = [{"role": "user", "content": "查询工单并根据结果决定下一步"}]
    trace = []
    failures = 0

    for step_number in range(1, max_steps + 1):
        # 把当前历史交给模型；模型可以检查上轮工具消息后改变决策。
        action = model(history)
        if not isinstance(action, Action):
            observation = {"ok": False, "error": "模型返回了非法动作结构"}
            history.append({"role": "tool", "name": "invalid_action", "call_id": step_number,
                            "content": observation})
            trace.append({"step": step_number, "name": "invalid_action", **observation})
            failures += 1
        elif action.name == "final":
            text = action.arguments.get("text") if isinstance(action.arguments, dict) else None
            if not isinstance(text, str) or not text.strip():
                observation = {"ok": False, "error": "最终回答必须是非空文本"}
                history.append({"role": "tool", "name": "invalid_final", "call_id": step_number,
                                "content": observation})
                trace.append({"step": step_number, "name": "invalid_final", **observation})
                failures += 1
            else:
                history.append({"role": "assistant", "content": text})
                return RunResult(text, "completed", history, trace)
        elif not isinstance(action.name, str) or not isinstance(action.arguments, dict):
            observation = {"ok": False, "error": "动作名称或参数格式非法"}
            history.append({"role": "tool", "name": "invalid_action", "call_id": step_number,
                            "content": observation})
            trace.append({"step": step_number, "name": "invalid_action", **observation})
            failures += 1
        elif action.name not in tools:
            observation = {"ok": False, "error": f"未知工具：{action.name}"}
            history.append({"role": "assistant", "tool_call": action.name,
                            "arguments": action.arguments, "call_id": step_number})
            history.append({"role": "tool", "name": action.name, "call_id": step_number,
                            "content": observation})
            trace.append({"step": step_number, "name": action.name, **observation})
            failures += 1
        else:
            history.append({"role": "assistant", "tool_call": action.name,
                            "arguments": action.arguments, "call_id": step_number})
            try:
                value = tools[action.name](**action.arguments)
                observation = {"ok": True, "value": value}
                failures = 0
            except ValueError:
                # 只把工具声明的业务输入错误转成受控观测，不暴露异常文本。
                observation = {"ok": False, "error": "工具拒绝了输入，请检查参数"}
                failures += 1
            history.append({"role": "tool", "name": action.name, "call_id": step_number,
                            "content": observation})
            trace.append({"step": step_number, "name": action.name, **observation})

        if failures >= max_consecutive_failures:
            return RunResult(None, "consecutive_failures", history, trace)

    return RunResult(None, "step_budget", history, trace)


def demo_model(history):
    """读取上轮观测：开放工单查询负责人，已关闭工单直接结束。"""
    observations = [message for message in history if message["role"] == "tool"]
    if not observations:
        return Action("lookup_ticket", {"ticket_id": "T-100"})

    latest = observations[-1]["content"]
    if not latest["ok"]:
        return Action("final", {"text": "查询失败，未执行后续业务动作。"})
    if observations[-1]["name"] == "lookup_ticket" and latest["value"]["status"] == "open":
        return Action("lookup_owner", {"ticket_id": latest["value"]["ticket_id"]})
    if observations[-1]["name"] == "lookup_ticket":
        return Action("final", {"text": f"工单状态为{latest['value']['status']}，无需通知。"})
    return Action("final", {"text": f"负责人：{latest['value']}。"})


def main():
    tools = {
        "lookup_ticket": lambda ticket_id: {"ticket_id": ticket_id, "status": "open"},
        "lookup_owner": lambda ticket_id: "Lin",
    }
    result = run_agent(demo_model, tools)
    print(f"结束原因：{result.reason}；最终回答：{result.answer}")
    for step in result.trace:
        print(f"第{step['step']}步 {step['name']}：{step}")


if __name__ == "__main__":
    main()
