"""服务器权威身份和复合键隔离；会话表是离线教学夹具。"""
SESSIONS = {"session-a": {"user": "alice", "tenant": "A", "roles": {"reader", "writer"}},
            "session-b": {"user": "bob", "tenant": "B", "roles": {"reader"}}}
TICKETS = {("A", "T-001"): "A企业：待处理", ("B", "T-001"): "B企业：已解决"}

def authenticate(session):
    if session not in SESSIONS:
        raise PermissionError("身份未认证")
    return SESSIONS[session]

def read_ticket(session, requested_tenant, ticket_id, cache, audit):
    principal = authenticate(session)
    allowed = requested_tenant == principal["tenant"] and "reader" in principal["roles"]
    # 审计记录结果与标识，不含凭证或工单正文。
    audit.append({"user": principal["user"], "tenant": principal["tenant"],
                  "action": "read", "resource": ticket_id, "allowed": allowed})
    if not allowed:
        raise PermissionError("租户或动作未授权")
    key = (principal["tenant"], ticket_id)
    if key not in cache:
        cache[key] = TICKETS.get(key)
    return cache[key]

def write_ticket(session, requested_tenant, ticket_id, state, approval, tickets, audit):
    """角色允许提出写操作，服务端审批记录另行绑定具体资源与目标状态。

    approval是调用方从可信审批存储读取的教学记录，绝不能直接取自客户端JSON。
    完整签发、期限、撤销与幂等协议见阶段43；这里只隔离角色与业务审批责任。
    """
    identity = authenticate(session)
    action = {"tenant": requested_tenant, "ticket_id": ticket_id, "state": state}
    allowed = (requested_tenant == identity["tenant"] and "writer" in identity["roles"]
               and isinstance(approval, dict) and approval == action)
    audit.append({"user": identity["user"], "tenant": identity["tenant"],
                  "action": "write", "resource": ticket_id, "allowed": allowed})
    if not allowed:
        raise PermissionError("角色、租户或业务审批不满足")
    if state not in {"open", "done"}:
        raise ValueError("工单状态不合法")
    key = (identity["tenant"], ticket_id)
    if key not in tickets:
        raise ValueError("工单不存在")
    tickets[key] = state  # 全部校验通过后才执行唯一一次写入。
    return state

if __name__ == "__main__":
    cache, audit = {}, []
    print("A结果：", read_ticket("session-a", "A", "T-001", cache, audit))
    print("B结果：", read_ticket("session-b", "B", "T-001", cache, audit))
    try:
        read_ticket("session-a", "B", "T-001", cache, audit)
    except PermissionError as error:
        print("伪造租户：", str(error))
    print("审计事件数：", len(audit))
