# 知识权限与冲突：默认标准库、离线、有限退出。
DOCS = [
    {"id": "hr", "department": "HR", "text": "薪资 私密"},
    {"id": "eng", "department": "ENG", "text": "排障 工单"},
    {"id": "public", "department": "*", "text": "工单 审批"},
]

def search(query, department, docs=DOCS):
    if department not in {"HR", "ENG"}:
        raise PermissionError("未知部门，默认拒绝")
    results = []
    for doc in docs:
        # 身份参数应由后端注入；例子不提供认证系统。
        if doc["department"] not in {department, "*"}:
            continue
        if set(query.split()) & set(doc["text"].split()):
            results.append(doc["id"])
    return results

def detect_conflict(facts):
    # 同一事实多种值时保留冲突，不随便选择模型更喜欢的一个。
    values = {fact["value"] for fact in facts}
    return len(values) > 1

def main():
    print(search("薪资 工单", "ENG"))
    print(detect_conflict([{"value": 500}, {"value": 800}]))

if __name__ == "__main__":
    main()
