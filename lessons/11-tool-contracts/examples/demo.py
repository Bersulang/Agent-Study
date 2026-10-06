"""只读工具契约；演示不包含身份系统，不能当完整权限实现。"""
TICKETS = {"T1": {"id": "T1", "status": "open"}}

TOOL_SPEC = {
    "name": "ticket_lookup",
    "description": "按工单id查询状态，不创建或修改工单",
    "parameters": {"type": "object", "properties": {"id": {"type": "string"}},
                   "required": ["id"], "additionalProperties": False},
}

def failure(code, message):
    return {"ok": False, "data": None,
            "error": {"code": code, "message": message, "retryable": False}}

def ticket_lookup(arguments):
    # 模型输出是不受信任输入，先校验再接触数据。
    if not isinstance(arguments, dict) or set(arguments) != {"id"}:
        return failure("invalid_arguments", "只接受id字段")
    identity = arguments["id"]
    if not isinstance(identity, str) or not identity.strip():
        return failure("invalid_arguments", "id必须非空字符串")
    if identity not in TICKETS:
        return failure("not_found", "工单不存在")
    # 返回副本，避免调用者通过结果改写数据源。
    return {"ok": True, "data": TICKETS[identity].copy(), "error": None}

TOOLS = {"ticket_lookup": ticket_lookup}

def dispatch(name, arguments):
    if not isinstance(name, str):
        return failure("unknown_tool", "工具名必须字符串")
    tool = TOOLS.get(name)
    if tool is None:
        return failure("unknown_tool", "未注册工具")
    return tool(arguments)

if __name__ == "__main__":
    print(dispatch("ticket_lookup", {"id": "T1"}))
    print(dispatch("ticket_lookup", {"id": 1}))
    print(dispatch("exec", {"command": "任意命令"}))
