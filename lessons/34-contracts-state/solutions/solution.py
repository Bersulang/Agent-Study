"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def merge_many(state, patches, expected_version):
    if expected_version != state["version"]:
        raise ValueError("version_conflict")
    candidate = dict(state)  # 先在副本构造，失败不影响原状态。
    for patch in patches:
        if set(patch) != {"status"} or patch["status"] not in {"ready", "blocked"}:
            raise ValueError("invalid_patch")
        candidate.update(patch)
    if patches:
        candidate["version"] += 1
    state.update(candidate)
    return dict(state)

if __name__ == "__main__":
    state = {"version": 1, "status": "new"}
    try:
        merge_many(state, [{"status": "ready"}, {"secret": "bad"}], 1)
    except ValueError:
        pass
    assert state == {"version": 1, "status": "new"}
    result = merge_many(state, [{"status": "blocked"}, {"status": "ready"}], 1)
    assert result == {"version": 2, "status": "ready"}
    print(result)
