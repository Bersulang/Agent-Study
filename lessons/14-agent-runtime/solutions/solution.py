"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    events = ["started"]
    used = 0
    reason = "completed"
    for step, name in enumerate(data["tools"]):
        if step == data.get("cancel_before_step"):
            reason = "cancelled"
            break
        if used >= 2:
            reason = "budget"
            break
        if name != "lookup":
            reason = "unknown_tool"
            break
        used += 1
        events.extend(["tool_started", "tool_completed"])
    events.append("stopped")
    return {"events": events, "used": used, "reason": reason}

if __name__ == "__main__":
    print(solve({"tools": ["lookup", "lookup"], "cancel_before_step": 1}))
