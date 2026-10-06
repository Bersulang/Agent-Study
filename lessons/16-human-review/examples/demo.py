"""审批内容绑定演示；审批对象假定来自受信任的人审服务。"""
import hashlib
import json

def action_digest(action):
    # 排序键与固定分隔符保证等价字典产生一致字节序列。
    payload = json.dumps(action, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def make_approval(action, decision="approve", now=0):
    if decision not in ("approve", "reject"):
        raise ValueError("审批决策必须为approve或reject")
    return {"digest": action_digest(action), "decision": decision,
            "expires_at": now + 60, "reviewer": "教学审核人"}

def authorized(action, approval, now=0):
    # 实际服务还要认证身份、查可信审批记录、撤销状态和单次消费。
    return (approval.get("decision") == "approve"
            and now < approval.get("expires_at", 0)
            and approval.get("digest") == action_digest(action))

def review_result(draft, evidence_ids):
    issues = []
    if not isinstance(draft.get("title"), str) or not draft["title"].strip():
        issues.append("标题缺失")
    if not evidence_ids:
        issues.append("没有可核查依据")
    return issues

if __name__ == "__main__":
    action = {"tool": "create_ticket", "args": {"title": "登录失败"}}
    approval = make_approval(action, now=10)
    print(f"原动作允许：{authorized(action, approval, now=11)}")
    edited = {"tool": "create_ticket", "args": {"title": "改过的标题"}}
    print(f"编辑后允许：{authorized(edited, approval, now=11)}")
    denied = make_approval(action, decision="reject", now=10)
    print(f"拒绝后允许：{authorized(action, denied, now=11)}")
    print(f"结果检查：{review_result({'title': '登录失败'}, [])}")
