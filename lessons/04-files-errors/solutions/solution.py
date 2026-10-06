"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
import json

def solve(data):
    tickets = json.loads(data)
    if not isinstance(tickets, list):
        raise ValueError("必须是列表")
    seen = set()
    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("工单必须是对象")
        identity = ticket.get("id")
        if not isinstance(identity, str) or not identity.strip():
            raise ValueError("id必须是非空字符串")
        if identity in seen:
            raise ValueError("id重复")
        seen.add(identity)
    return len(tickets)

if __name__ == "__main__":
    print(f"记录数：{solve('[{"id": "T1"} ]')}")
    try:
        solve('[{"id":"T1"},{"id":"T1"}]')
    except ValueError as error:
        print(f"拒绝：{error}")
