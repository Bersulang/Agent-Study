# 受预算控制的Agentic RAG：默认标准库、离线、有限退出。
KNOWLEDGE = {"发票": "需要有效发票", "审批": "付款前主管审批"}

def research(topics, budget=2):
    if budget < 0:
        raise ValueError("预算不能为负")
    evidence, trace = {}, []
    for topic in topics:
        # 已取得的证据复用，不为重复子问题消耗预算。
        if topic in evidence:
            continue
        if len(trace) >= budget:
            break
        trace.append({"query": topic, "step": len(trace) + 1})
        if topic in KNOWLEDGE:
            evidence[topic] = KNOWLEDGE[topic]
    missing = [topic for topic in dict.fromkeys(topics) if topic not in evidence]
    return {"status": "complete" if not missing else "partial",
            "evidence": evidence, "missing": missing, "trace": trace}

def main():
    print(research(["发票", "审批", "期限"], budget=2))

if __name__ == "__main__":
    main()
