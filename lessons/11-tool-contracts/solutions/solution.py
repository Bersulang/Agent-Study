"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    def error(code):
        return {"ok": False, "data": None, "error": {"code": code, "retryable": False}}
    if data.get("name") != "ticket_search":
        return error("unknown_tool")
    arguments = data.get("args")
    if not isinstance(arguments, dict) or set(arguments) != {"status"}:
        return error("invalid_arguments")
    if arguments["status"] not in ("open", "closed"):
        return error("invalid_arguments")
    rows = [{"id": "T1", "status": "open"}, {"id": "T2", "status": "closed"}]
    result = [row.copy() for row in rows if row["status"] == arguments["status"]]
    return {"ok": True, "data": result, "error": None}

if __name__ == "__main__":
    print(solve({"name": "ticket_search", "args": {"status": "open"}}))
    print(solve({"name": "ticket_search", "args": {"status": "unknown"}}))
