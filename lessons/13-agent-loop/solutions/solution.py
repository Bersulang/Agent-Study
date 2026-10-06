"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    trace = []
    for step, action in enumerate(data):
        if step >= 3:
            return {"reason": "step_budget", "trace": trace}
        if not isinstance(action, dict):
            return {"reason": "invalid_action", "trace": trace}
        if action.get("type") == "final":
            text = action.get("text")
            if not isinstance(text, str) or not text.strip():
                return {"reason": "invalid_final", "trace": trace}
            return {"reason": "completed", "trace": trace, "answer": text}
        if action.get("name") != "search":
            return {"reason": "unknown_tool", "trace": trace}
        query = action.get("args", {}).get("query")
        if not isinstance(query, str) or not query.strip():
            return {"reason": "invalid_arguments", "trace": trace}
        # 固定知识夹具，不能视为真实检索服务。
        trace.append({"query": query, "evidence": "policy-v1"})
    return {"reason": "model_exhausted", "trace": trace}

if __name__ == "__main__":
    print(solve([{"name": "search", "args": {"query": "VPN"}}, {"type": "final", "text": "依据policy-v1"}]))
