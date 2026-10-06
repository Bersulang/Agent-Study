# 本地MCP接入：默认标准库、离线、有限退出。
TOOLS = {"get_ticket": {"description": "查询工单", "required": ["ticket_id"]}}
TICKETS = {"T1": {"status": "open", "title": "登录失败"}}

def dispatch(request):
    # 教学协议子集，只模拟发现和调用；不实现MCP初始化或JSON-RPC传输。
    method = request.get("method")
    if method == "tools/list":
        return {"tools": TOOLS}
    if method != "tools/call":
        raise ValueError("不支持的方法")
    params = request.get("params", {})
    if params.get("name") != "get_ticket":
        raise ValueError("未知工具")
    identity = params.get("arguments", {}).get("ticket_id")
    if not isinstance(identity, str) or not identity:
        raise ValueError("ticket_id必须是非空字符串")
    ticket = TICKETS.get(identity)
    return {"found": ticket is not None, "ticket": dict(ticket) if ticket else None}

def main():
    print(dispatch({"method": "tools/list"}))
    print(dispatch({"method": "tools/call", "params": {"name": "get_ticket", "arguments": {"ticket_id": "T1"}}}))

if __name__ == "__main__":
    main()
