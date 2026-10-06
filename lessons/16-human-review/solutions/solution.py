"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
import hashlib
import json

def solve(data):
    action = data["action"]
    approval = data["approval"]
    args = action.get("args")
    if action.get("tool") != "create_ticket" or not isinstance(args, dict):
        return {"decision": "blocked", "reason": "invalid_action"}
    if set(args) != {"title"} or not isinstance(args["title"], str) or not args["title"].strip():
        return {"decision": "blocked", "reason": "invalid_arguments"}
    if approval.get("decision") != "approve":
        return {"decision": "blocked", "reason": "not_approved"}
    if data["now"] >= approval.get("expires_at", 0):
        return {"decision": "blocked", "reason": "expired"}
    digest = hashlib.sha256(json.dumps(action, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != approval.get("digest"):
        return {"decision": "blocked", "reason": "changed_action"}
    return {"decision": "execute", "reason": "approved"}

def inspect_once(draft, evidence, revised=None):
    # 至多接受一份修订；没有依据时即使title已修复也转人工。
    candidate = draft
    if not candidate.get("title") and revised is not None:
        candidate = revised
    if not candidate.get("title") or not evidence:
        return "human_review"
    return "ready_for_approval"

if __name__ == "__main__":
    action = {"tool": "create_ticket", "args": {"title": "登录失败"}}
    print(solve({"action": action, "approval": {"decision": "reject"}, "now": 1}))
    print(inspect_once({}, [], revised={"title": "登录失败"}))
