"""协作总预算：重试消耗全局预算，永久错误停止，已完成任务去重。"""
class TemporaryFailure(Exception):
    """暂时失败且本次未生效，才允许自动重试。"""

def cooperate(actions, budget):
    completed = {}
    attempts = 0
    effects = 0
    for key, outcomes in actions:
        if key in completed:
            continue
        for outcome in outcomes:
            if attempts >= budget:
                return {"status": "budget_exhausted", "attempts": attempts, "effects": effects}
            attempts += 1
            try:
                if outcome == "temporary":
                    raise TemporaryFailure("本次尚未产生副作用")
                if outcome == "denied":
                    return {"status": "permanent_failure", "attempts": attempts, "effects": effects}
                effects += 1
                completed[key] = "done"
                break
            except TemporaryFailure:
                continue
        else:
            return {"status": "budget_exhausted", "attempts": attempts, "effects": effects}
    return {"status": "completed", "attempts": attempts, "effects": effects}

def run_case(case):
    if case == "budget":
        return cooperate([("close-T7", ["temporary"] * 5)], budget=2)
    if case == "permanent":
        return cooperate([("close-T7", ["denied", "ok"])], budget=2)
    return cooperate([("close-T7", ["temporary", "ok"]), ("close-T7", ["ok"])], budget=3)

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'budget', 'permanent']:
        print(case, run_case(case))
