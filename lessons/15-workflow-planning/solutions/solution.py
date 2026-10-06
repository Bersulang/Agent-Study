"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    trace = ["received"]
    if not data.get("allowed", False):
        return {"state": "denied", "trace": trace + ["denied"]}
    query = data.get("query")
    if not isinstance(query, str) or not query.strip():
        return {"state": "clarify", "trace": trace + ["clarify"]}
    trace.append("search")
    evidence = data.get("evidence", False)
    if not evidence:
        trace.extend(["query_rewrite", "search"])
        # 重写后的证据也是固定夹具，教学中不调用真实检索服务。
        evidence = data.get("rewritten_evidence", False)
    state = "answered" if evidence else "human_review"
    return {"state": state, "trace": trace + [state]}

if __name__ == "__main__":
    print(solve({"query": "VPN", "allowed": True, "rewritten_evidence": True}))
    print(solve({"query": "VPN", "allowed": False}))
