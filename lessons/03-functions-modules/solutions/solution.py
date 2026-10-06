"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    # sorted返回新列表；key函数只告诉排序器比较哪个字段。
    minimum = data.get("minimum", 3)
    chosen = []
    for ticket in data["tickets"]:
        if ticket["priority"] >= minimum:
            chosen.append(ticket)
    def priority(ticket):
        return ticket["priority"]
    # 此阶段先用普通循环；阶段05会系统讲解列表推导式。
    identities = []
    for item in sorted(chosen, key=priority, reverse=True):
        identities.append(item["id"])
    return identities

if __name__ == "__main__":
    print(solve({"tickets": [{"id": "T1", "priority": 3}, {"id": "T2", "priority": 5}]}))
    print(solve({"tickets": []}))
