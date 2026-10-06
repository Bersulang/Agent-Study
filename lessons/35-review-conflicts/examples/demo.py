"""生成与核验分离：检查引用支持主张，并识别同级证据冲突。"""
def review(draft, evidence):
    values = {item["value"] for item in evidence}
    if len(values) != 1:
        return {"accepted": False, "reason": "conflicting_evidence"}
    citations = {item["id"] for item in evidence}
    if draft["citation"] not in citations or draft["value"] not in values:
        return {"accepted": False, "reason": "unsupported_claim"}
    return {"accepted": True, "reason": None}

def revise(evidence, max_rounds=2):
    draft = {"value": 99, "citation": "missing"}
    for round_number in range(max_rounds + 1):
        verdict = review(draft, evidence)
        if verdict["accepted"]:
            return {"status": "accepted", "rounds": round_number, "citation": draft["citation"]}
        if round_number == max_rounds:
            break
        # 模拟修订只取一条证据。冲突不会因重复生成而自动消失。
        draft = {"value": evidence[0]["value"], "citation": evidence[0]["id"]}
    return {"status": "human_review", "rounds": max_rounds, "citation": None}

def run_case(case):
    evidence = [{"id": "policy-v2", "value": 7}]
    if case == "conflict":
        evidence.append({"id": "policy-v2-other", "value": 14})
    return revise(evidence)

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'conflict']:
        print(case, run_case(case))
