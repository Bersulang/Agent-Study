"""脚本模型模拟Agent循环；只验证执行机制。"""
def lookup(arguments):
    if not isinstance(arguments, dict) or set(arguments) != {"id"}:
        raise ValueError("查询需要且只接受id")
    if arguments["id"] != "T1":
        raise ValueError("工单不存在")
    return {"id": "T1", "status": "open"}

TOOLS = {"lookup": lookup}

def run(actions, max_steps=4):
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("步数必须为正整数")
    observations = []
    failures = 0
    for step, action in enumerate(actions):
        if step >= max_steps:
            return {"reason": "step_budget", "observations": observations}
        if not isinstance(action, dict):
            return {"reason": "invalid_action", "observations": observations}
        if action.get("type") == "final":
            text = action.get("text")
            if not isinstance(text, str) or not text.strip():
                return {"reason": "invalid_action", "observations": observations}
            return {"reason": "completed", "answer": text, "observations": observations}
        if action.get("type") != "tool":
            return {"reason": "invalid_action", "observations": observations}
        name = action.get("name")
        tool = TOOLS.get(name) if isinstance(name, str) else None
        try:
            if tool is None:
                raise ValueError("未知工具")
            data = tool(action.get("args"))
            observations.append({"ok": True, "data": data})
            failures = 0
        except ValueError as error:
            observations.append({"ok": False, "error": str(error)})
            failures += 1
        if failures >= 2:
            return {"reason": "consecutive_failures", "observations": observations}
    return {"reason": "model_exhausted", "observations": observations}

if __name__ == "__main__":
    actions = [{"type": "tool", "name": "lookup", "args": {"id": "T1"}},
               {"type": "final", "text": "[脚本模型]T1仍在处理中"}]
    print(run(actions))
    print(run([{"type": "tool", "name": "exec", "args": {}}] * 3))
