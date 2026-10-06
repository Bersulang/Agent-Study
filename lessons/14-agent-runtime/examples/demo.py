"""最小同步Runtime；事件与状态只在内存中，不是持久化框架。"""
def lookup():
    return {"id": "T1", "status": "open"}

TOOLS = {"lookup": lookup}

def before_tool(state, cancelled):
    # 中间件只决定能否开始，尚未产生业务副作用。
    if cancelled():
        return "cancelled"
    if state["used"] >= state["budget"]:
        return "budget"
    return None

def execute(names, budget=3, cancelled=lambda: False):
    if type(budget) is not int or budget < 0:
        raise ValueError("预算必须是非负整数")
    state = {"status": "running", "used": 0, "budget": budget,
             "messages": [], "events": [{"type": "started"}], "reason": None}
    for step, name in enumerate(names):
        reason = before_tool(state, cancelled)
        if reason:
            state["reason"] = reason
            break
        tool = TOOLS.get(name) if isinstance(name, str) else None
        if tool is None:
            state["reason"] = "unknown_tool"
            break
        state["used"] += 1
        state["events"].append({"type": "tool_started", "step": step, "name": name})
        try:
            result = tool()
        except Exception as error:
            # Runtime边界转换为明确终止；记录类型而不泄露敏感异常正文。
            state["events"].append({"type": "tool_failed", "step": step, "error_type": type(error).__name__})
            state["reason"] = "tool_error"
            break
        state["messages"].append({"role": "tool", "name": name, "content": result})
        state["events"].append({"type": "tool_completed", "step": step})
    if state["reason"] is None:
        state["reason"] = "completed"
    state["status"] = "stopped"
    state["events"].append({"type": "stopped", "reason": state["reason"]})
    return state

if __name__ == "__main__":
    state = execute(["lookup", "lookup"], budget=1)
    print(f"状态：{state['status']}；停止原因：{state['reason']}；已用预算：{state['used']}")
    print(f"事件：{[event['type'] for event in state['events']]}")
    print(f"提前取消：{execute(['lookup'], cancelled=lambda: True)['reason']}")
