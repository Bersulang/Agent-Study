"""交接转移对话控制权，事实通过白名单缩减。"""
def handoff(owner, target, facts, history, max_hops=3):
    selected = {key: facts[key] for key in ("ticket_id",) if key in facts}
    # history 是已拥有控制权的角色路径；先检查再改变 owner。
    if target in history:
        return {"owner": owner, "facts": selected, "status": "loop_blocked"}
    if len(history) - 1 >= max_hops:
        return {"owner": owner, "facts": selected, "status": "hop_limit"}
    if target != "ticket" or "ticket_id" not in selected:
        raise ValueError("接收者或必要事实不符合交接契约")
    return {"owner": target, "facts": selected, "status": "transferred"}

def run_case(case):
    facts = {"ticket_id": "T-7", "private_note": "不应传给另一角色"}
    history = ["reception"]
    if case == "loop":
        history = ["reception", "ticket", "reception"]
    if case == "limit":
        history = ["reader", "reviewer", "helper", "reception"]
    return handoff("reception", "ticket", facts, history)

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'loop', 'limit']:
        print(case, run_case(case))
