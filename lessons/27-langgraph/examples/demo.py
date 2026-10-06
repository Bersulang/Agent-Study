# LangGraph状态与中断：默认标准库、离线、有限退出。
def step(state, decision=None):
    # 复制状态避免调用者无意被修改；这里只做浅复制，嵌套对象需另行设计。
    next_state = dict(state)
    if state["stage"] == "draft":
        next_state["stage"] = "waiting"
    elif state["stage"] == "waiting":
        if decision is None:
            return next_state
        if not isinstance(decision, bool):
            raise ValueError("审批决定必须为布尔值")
        next_state["approved"] = decision
        next_state["stage"] = "done" if decision else "rejected"
    elif state["stage"] not in {"done", "rejected"}:
        raise ValueError("未知状态")
    return next_state

def main():
    state = step({"stage": "draft", "task": "T1"})
    print(state)
    print(step(state, False))

if __name__ == "__main__":
    main()
