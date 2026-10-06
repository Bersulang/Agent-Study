"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    records = {}
    tickets = []
    for request in data:
        key, title = request["key"], request["title"]
        if not isinstance(key, str) or not key.strip():
            raise ValueError("无效键")
        if not isinstance(title, str) or not title.strip() or len(title) > 100:
            raise ValueError("无效标题")
        if key in records:
            if records[key]["title"] != title:
                raise ValueError("键参数冲突")
            continue
        ticket = {"id": f"T{len(tickets) + 1}", "title": title}
        records[key] = ticket
        tickets.append(ticket)
    return tickets

if __name__ == "__main__":
    print(solve([{"key": "k1", "title": "故障"}, {"key": "k1", "title": "故障"}]))
