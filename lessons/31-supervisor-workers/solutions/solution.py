"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def summarize_required(tasks, results):
    required = {task["id"] for task in tasks if task.get("required", True)}
    optional = {task["id"] for task in tasks if not task.get("required", True)} - required
    missing = sorted(key for key in required if results.get(key) is None)
    warnings = sorted(key for key in optional if results.get(key) is None)
    return {"status": "blocked" if missing else "completed", "missing": missing, "warnings": warnings}

if __name__ == "__main__":
    tasks = [{"id": "policy"}, {"id": "ticket"}, {"id": "suggestion", "required": False}]
    assert summarize_required(tasks, {"policy": "v2"})["missing"] == ["ticket"]
    result = summarize_required(tasks, {"policy": "v2", "ticket": "T-7"})
    assert result == {"status": "completed", "missing": [], "warnings": ["suggestion"]}
    print(result)
