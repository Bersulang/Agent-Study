"""主控委派：子任务有稳定标识、深度限制和缺失结果检查。"""
def supervise(tasks, workers, depth=0, max_depth=2):
    if depth >= max_depth:
        return {"status": "depth_exceeded", "calls": 0, "missing": []}
    seen = set()
    results = {}
    calls = 0
    for task in tasks:
        key = task["id"]
        if key in seen:
            continue  # 相同逻辑任务只委派一次，避免重复副作用。
        seen.add(key)
        worker = workers.get(task["role"])
        if worker is not None:
            calls += 1
            value = worker(task)
            if value is not None:
                results[key] = value
    # 完成条件来自原始计划，不能把已有结果数量误当全部成功。
    missing = sorted(seen - results.keys())
    return {"status": "incomplete" if missing else "completed", "calls": calls, "missing": missing}

def run_case(case):
    tasks = [{"id": "knowledge", "role": "reader"}, {"id": "ticket", "role": "ticket"}]
    tasks.append(dict(tasks[0]))  # 人为制造重复委派请求。
    workers = {"reader": lambda task: "policy-v2", "ticket": lambda task: "T-7"}
    if case == "missing":
        workers["ticket"] = lambda task: None
    return supervise(tasks, workers, depth=2 if case == "depth" else 0)

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'missing', 'depth']:
        print(case, run_case(case))
