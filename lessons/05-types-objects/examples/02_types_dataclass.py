"""类型标注帮助阅读；数据类不自动验证输入。"""
from dataclasses import dataclass


@dataclass
class Ticket:
    ticket_id: str
    priority: int

    def __post_init__(self):
        # 边界校验必须显式写，bool虽然是int子类但不应作优先级。
        if not isinstance(self.ticket_id, str) or not self.ticket_id.strip():
            raise ValueError("工单编号必须是非空文本")
        if type(self.priority) is not int or not 1 <= self.priority <= 5:
            raise ValueError("优先级必须是1到5的整数")


if __name__ == "__main__":
    print(Ticket("T-2", 3))
