"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
from dataclasses import dataclass

@dataclass
class Ticket:
    id: str
    priority: int

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("无效id")
        if type(self.priority) is not int or not 1 <= self.priority <= 5:
            raise ValueError("无效priority")

def solve(data):
    # 先验证全部记录，再筛选，避免坏记录被筛选条件隐藏。
    tickets = [Ticket(row["id"], row["priority"]) for row in data]
    return [(ticket.id, ticket.priority) for ticket in tickets if ticket.priority >= 4]

if __name__ == "__main__":
    print(solve([{"id": "T1", "priority": 5}]))
    try:
        solve([{"id": "T2", "priority": True}])
    except ValueError as error:
        print(f"拒绝：{error}")
