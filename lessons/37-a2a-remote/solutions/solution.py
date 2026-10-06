"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def cancel_terminal(registry, task_id):
    task = registry.get(task_id)
    if "error" in task:
        return {"status": "not_found"}
    if task["status"] in {"completed", "canceled"}:
        return {"status": "not_cancelable"}
    registry.cancel(task_id)
    return {"status": "canceled"}

if __name__ == "__main__":
    registry = demo.TaskRegistry()
    registry.submit("task-7", "工单")
    registry.finish("task-7")
    assert cancel_terminal(registry, "missing")["status"] == "not_found"
    result = cancel_terminal(registry, "task-7")
    assert result["status"] == "not_cancelable"
    assert registry.get("task-7")["artifact"] == "T-7: open"
    print(result)
