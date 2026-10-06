"""需求规则演示：没有模型，输出是规则决策。"""
def decide(request):
    intent = request.get("intent")
    if intent == "lookup_ticket":
        if not request.get("id"):
            return "clarify"
        if not request.get("can_read", False):
            return "deny"
        return "read_only"
    if intent == "create_ticket":
        return "draft_for_review"
    return "human_handoff"

def evaluate(cases):
    correct = 0
    for request, expected in cases:
        actual = decide(request)
        correct += actual == expected
        print(f"预期={expected} 实际={actual}")
    return correct, len(cases)

if __name__ == "__main__":
    cases = [
        ({"intent": "lookup_ticket"}, "clarify"),
        ({"intent": "lookup_ticket", "id": "T1", "can_read": False}, "deny"),
        ({"intent": "create_ticket"}, "draft_for_review"),
        ({"intent": "unknown"}, "human_handoff"),
    ]
    correct, total = evaluate(cases)
    print(f"规则案例：{correct}/{total}；不代表模型质量")
