"""类型标注服务于阅读；校验必须显式执行。"""
from dataclasses import dataclass
from functools import wraps

def traced(function):
    # @wraps保留名称，包装器把调用转交给原函数。
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"调用：{function.__name__}")
        return function(*args, **kwargs)
    return wrapper

@dataclass
class Ticket:
    id: str
    priority: int

    def __post_init__(self):
        # dataclass不会自动验证类型；拒绝bool充当整数优先级。
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id不能为空")
        if type(self.priority) is not int or not 1 <= self.priority <= 5:
            raise ValueError("priority必须是1到5的整数")

class Repository:
    def __init__(self, tickets):
        self.tickets = list(tickets)

    @traced
    def urgent(self):
        for ticket in self.tickets:
            if ticket.priority >= 4:
                # yield暂停在这里，下次迭代继续for。
                yield ticket

if __name__ == "__main__":
    repository = Repository([Ticket("T1", 5), Ticket("T2", 2)])
    identities = [ticket.id for ticket in repository.urgent()]
    identity, priority = ("T1", 5)
    print(f"紧急：{identities}；解包：{identity}/{priority}")
