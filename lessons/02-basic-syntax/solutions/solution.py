"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    # 结果容器独立创建，不在原字典写入统计字段。
    result = {"open_ids": [], "by_department": {}}
    for ticket in data:
        if ticket["status"] == "open":
            result["open_ids"].append(ticket["id"])
            department = ticket["department"]
            counts = result["by_department"]
            counts[department] = counts.get(department, 0) + 1
    return result

if __name__ == "__main__":
    print(solve([{"id": "T9", "department": "IT", "status": "open"}]))
    print(solve([]))
