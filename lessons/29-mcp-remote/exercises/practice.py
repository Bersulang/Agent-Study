# 独立练习骨架：请按exercises/README.md的函数契约完成，不要复制参考答案。
def solve(required, discovered):
    """实现本阶段业务行为；自动检查使用与阶段参考接口兼容的参数。"""
    raise NotImplementedError("请按练习要求实现solve(required, discovered)")


def call_read(operation, attempts=2):
    """实现只读操作的有限断连重试；写请求不应复用此函数。"""
    raise NotImplementedError("请实现有限只读重试")

if __name__ == "__main__":
    print("请先实现solve函数，统一校验会使用独立输入调用它。")
