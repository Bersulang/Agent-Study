# 带引用的基础RAG：默认标准库、离线、有限退出。
DOCUMENTS = [
    {"id": "policy:1", "text": "报销 发票 审批", "source": "policy.md#1"},
    {"id": "security:1", "text": "密码 重置 工单", "source": "security.md#1"},
]

def retrieve(query, documents=DOCUMENTS):
    # 教学词项重叠检索，不是语义embedding；空格分词便于观察计分。
    terms = set(query.split())
    scored = []
    for doc in documents:
        score = len(terms & set(doc["text"].split()))
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [doc for score, doc in scored[:2]]

def answer(query):
    hits = retrieve(query)
    if not hits:
        return {"status": "no_evidence", "answer": "资料中没有足够证据", "citations": []}
    # 只摘录命中的证据；没有调用语言模型，不能声称生成式问答质量。
    return {"status": "supported", "answer": hits[0]["text"],
            "citations": [hits[0]["source"]]}

def main():
    print(answer("报销 发票"))
    print(answer("工资"))

if __name__ == "__main__":
    main()
