"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
def solve(data):
    usage = data["usage"]
    for key in ("input_tokens", "output_tokens"):
        if type(usage.get(key)) is not int or usage[key] < 0:
            raise ValueError("token数量必须是非负整数")
    input_rate = data.get("input_rate", 1)
    output_rate = data.get("output_rate", 2)
    budget = data["budget"]
    if min(input_rate, output_rate, budget) < 0:
        raise ValueError("费率与预算不能为负")
    cost = (usage["input_tokens"] * input_rate + usage["output_tokens"] * output_rate) / 1_000_000
    return {"cost": cost, "decision": "allow" if cost <= budget else "deny"}

if __name__ == "__main__":
    print(solve({"usage": {"input_tokens": 100, "output_tokens": 50}, "budget": 0.001}))
