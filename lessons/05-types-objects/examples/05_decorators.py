"""先会读和使用装饰器；之后再尝试自己编写。"""
from functools import wraps


def log_call(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"调用 {function.__name__}")
        # 包装函数返回原函数结果，保持调用者可观察到的行为。
        return function(*args, **kwargs)
    return wrapper


@log_call
def ticket_count(tickets):
    return len(tickets)


if __name__ == "__main__":
    print(ticket_count(["T-1", "T-2"]))
