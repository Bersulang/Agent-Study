"""从基础容器表示工单，不引入类型标注或推导式。"""
# 列表中的每个字典代表一个工单；冒号分隔键和值。
tickets = [
    {"id": "T1", "department": "IT", "priority": 5, "status": "open"},
    {"id": "T2", "department": "HR", "priority": 4, "status": "closed"},
    {"id": "T3", "department": "IT", "priority": 2, "status": "open"},
]
urgent = []
departments = set()
for ticket in tickets:
    # 用集合去重，列表保留筛选结果的输入顺序。
    departments.add(ticket["department"])
    if ticket["status"] != "closed" and ticket["priority"] >= 4:
        urgent.append(ticket["id"])
print(f"紧急工单：{urgent}")
print(f"部门：{sorted(departments)}")
# 赋值共享列表；这里只复制一层字典，字段都是不可变值。
alias = tickets
snapshot = tickets[0].copy()
alias[0]["status"] = "assigned"
print(f"原记录：{tickets[0]['status']}；快照：{snapshot['status']}")
pair = (tickets[0]["id"], snapshot["status"])
print(f"不可变字段组合：{pair}")
