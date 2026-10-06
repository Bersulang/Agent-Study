# 检索优化与定位失败：默认标准库、离线、有限退出。
DOCS = [{"id": "A", "text": "报销 发票", "active": True},
        {"id": "B", "text": "报销 审批", "active": True},
        {"id": "C", "text": "报销 发票 旧版", "active": False}]

def search(query, docs=DOCS):
    aliases = {"差旅": "报销", "凭证": "发票"}
    raw = set(query.split())
    expanded = raw | {aliases[word] for word in raw if word in aliases}
    ranked = []
    for doc in docs:
        # 过滤在候选生成之前执行，旧政策不能靠高分重新进入结果。
        if not doc["active"]:
            continue
        words = set(doc["text"].split())
        score = 2 * len(raw & words) + len(expanded & words)
        if score:
            ranked.append((score, doc["id"]))
    return [identity for score, identity in sorted(ranked, key=lambda x: (-x[0], x[1]))]

def metrics(expected, actual):
    relevant = set(expected)
    returned = set(actual)
    correct = len(relevant & returned)
    return {"recall": correct / len(relevant) if relevant else 0.0,
            "precision": correct / len(returned) if returned else 0.0}

def main():
    print(search("差旅 凭证"))
    print(metrics(["A", "B"], ["A"]))

if __name__ == "__main__":
    main()
