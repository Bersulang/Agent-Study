"""可复用业务模块：导入时只定义函数，不打印演示结果。"""

def select(tickets, minimum=4):
    # 局部结果每次调用重新创建，互不共享。
    result = []
    for ticket in tickets:
        if ticket["priority"] >= minimum:
            result.append(ticket["id"])
    return result


def add_tag(name, tags=None):
    # None表示未提供；复制外层列表避免修改调用者的数据。
    if tags is None:
        tags = []
    else:
        tags = list(tags)
    tags.append(name)
    return tags
