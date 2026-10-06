# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(state, approval):
    if state["stage"] != "waiting":
        raise ValueError("仅等待状态可以接收审批")
    if approval["task"] != state["task"] or approval["digest"] != state["digest"]:
        raise PermissionError("审批没有绑定当前动作")
    return demo.step(state, approval["decision"])

print(solve({"stage": "waiting", "task": "T1", "digest": "v1"},
            {"task": "T1", "digest": "v1", "decision": False}))
