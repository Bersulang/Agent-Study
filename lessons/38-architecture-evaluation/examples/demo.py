"""同一数据集对比架构；预算使用逻辑单位，不伪称模型延迟基准。"""
FIXTURES = [("政策", "policy-v2"), ("工单", "T-7"), ("政策和工单", "policy-v2 / T-7")]

def single(question):
    # 单职责实现会遗漏组合问题，不代表所有单 Agent 都有此限制。
    return "policy-v2" if "政策" in question else "T-7"

def workflow(question, broken=False):
    if question == "政策和工单":
        return None if broken else "policy-v2 / T-7"
    return single(question)

def multi(question):
    parts = []
    if "政策" in question:
        parts.append("policy-v2")
    if "工单" in question:
        parts.append("T-7")
    return " / ".join(parts)

def evaluate(broken=False):
    implementations = {"single": single, "workflow": lambda q: workflow(q, broken), "multi": multi}
    # 手工成本表是教学预算，测真实成本应记录实际调用和 token。
    costs = {"single": 1, "workflow": 2, "multi": 4}
    scores = {}
    for name, implementation in implementations.items():
        scores[name] = sum(implementation(q) == expected for q, expected in FIXTURES)
    eligible = [name for name in scores if scores[name] == len(FIXTURES)]
    selected = min(eligible, key=lambda name: costs[name]) if eligible else "none"
    return {"single_correct": scores["single"], "workflow_correct": scores["workflow"],
            "multi_correct": scores["multi"], "selected": selected}

def run_case(case):
    return evaluate(broken=case == "regression")

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['comparison', 'regression']:
        print(case, run_case(case))
