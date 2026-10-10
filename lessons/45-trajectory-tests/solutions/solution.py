"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

# 两种轨迹都声称任务结束，但未审批写入必须拒绝；最终答案不能替代执行证据。
assert api["validate_trace"](["started", "read", "finished"])["writes"] == 0
assert api["validate_trace"](["started", "approved", "write", "finished"])["writes"] == 1
invalid = [
    (["started", "write", "finished"], PermissionError),
    (["started", "approved", "write", "write", "finished"], ValueError),
    (["started", "approved", "revoked", "write", "finished"], PermissionError),
    (["started", "finished", "read"], ValueError),
]
for trace, expected_error in invalid:
    try:
        api["validate_trace"](trace)
    except expected_error as error:
        print("拒绝轨迹：", trace, str(error))
    else:
        raise AssertionError("违规轨迹被错误接受")

def solve(data):
    """检查离线轨迹中审批、撤销和终态对写动作的约束。"""
    approved, revoked, finished = False, False, bool(data.get("finished", False))
    reads = writes = 0
    violations = []
    for event in data["events"]:
        if finished:
            if event in {"read", "write"}: violations.append("finished_task")
            continue
        if event == "approved": approved, revoked = True, False
        elif event == "revoked": revoked = True
        elif event == "read": reads += 1
        elif event == "write":
            if approved and not revoked: writes += 1
            else: violations.append("write_without_current_approval")
        elif event == "finished": finished = True
    return {"allowed_reads": reads, "allowed_writes": writes, "violations": violations}
