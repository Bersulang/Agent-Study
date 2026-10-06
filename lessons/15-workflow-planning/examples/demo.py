"""固定工作流加一次受限重规划；没有真实模型规划。"""
DEPENDENCIES = {"search": set(), "answer": {"search"}, "human_review": {"search"}}

def workflow(query, evidence=True, max_replans=1):
    if type(max_replans) is not int or max_replans < 0:
        raise ValueError("重规划预算必须为非负整数")
    state = {"state": "received", "history": ["received"], "replans": 0, "completed": []}
    if query not in ("登录", "VPN"):
        state["state"] = "clarify"
        state["history"].append("clarify")
        return state
    state["history"].append("routed")
    plan = ["search", "answer"]
    while plan:
        step = plan.pop(0)
        # 依赖由程序检查，不能信任规划器输出的顺序。
        if not DEPENDENCIES[step] <= set(state["completed"]):
            raise ValueError("步骤依赖未满足")
        if step == "search":
            state["completed"].append("search")
            state["history"].append("retrieved")
            if not evidence:
                if state["replans"] >= max_replans:
                    state["state"] = "stopped"
                    state["history"].append("stopped")
                    return state
                state["replans"] += 1
                # 只替换未执行部分；已经发生的search不重做。
                plan = ["human_review"]
                state["history"].append("replanned")
        elif step == "answer":
            state["state"] = "answered"
            state["history"].append("answered")
        else:
            state["state"] = "human_review"
            state["history"].append("human_review")
    return state

if __name__ == "__main__":
    for evidence in (True, False):
        result = workflow("登录", evidence=evidence)
        print(f"证据={evidence}；终态={result['state']}；轨迹={result['history']}")
    print(f"未知问题终态：{workflow('其他')['state']}")
