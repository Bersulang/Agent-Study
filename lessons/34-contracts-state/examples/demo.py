"""显式结果契约与乐观并发版本，拒绝非法字段后不部分更新。"""
def merge(state, patch, expected_version):
    if expected_version != state["version"]:
        raise ValueError("version_conflict")
    # 必须校验整个补丁，避免前半部分已写入、后半部分才发现越权。
    if set(patch) != {"status"} or patch["status"] not in {"ready", "blocked"}:
        raise ValueError("invalid_patch")
    state.update(patch)
    state["version"] += 1
    return dict(state)  # 返回拷贝，避免外部修改内部共享字典。

def run_case(case):
    state = {"version": 1, "status": "new"}
    try:
        if case == "invalid":
            merge(state, {"status": "ready", "private_reason": "leak"}, 1)
        else:
            merge(state, {"status": "ready"}, 1)
            if case == "conflict":
                merge(state, {"status": "blocked"}, 1)
    except ValueError as exc:
        return {**state, "error": str(exc)}
    return state

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'conflict', 'invalid']:
        print(case, run_case(case))
