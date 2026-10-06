"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    decisions = []
    for request in data:
        if request.get("intent") != "policy_question":
            decisions.append("clarify")
        elif not request.get("can_read", False):
            decisions.append("deny")
        elif not request.get("evidence"):
            decisions.append("human_handoff")
        else:
            decisions.append("answer")
    return decisions

if __name__ == "__main__":
    # 固定六个验收案例，预期策略独立于函数实现。
    cases = [
        ({"intent": "policy_question", "can_read": True, "evidence": "policy-v1"}, "answer"),
        ({"intent": "policy_question", "can_read": True}, "human_handoff"),
        ({"intent": "policy_question", "can_read": False, "evidence": "policy-v1"}, "deny"),
        ({"intent": "policy_question"}, "deny"),
        ({"intent": "other"}, "clarify"),
        ({}, "clarify"),
    ]
    actual = solve([case[0] for case in cases])
    expected = [case[1] for case in cases]
    print(f"决策：{actual}")
    print(f"固定案例符合预期：{actual == expected}")
