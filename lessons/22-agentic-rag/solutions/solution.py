# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(topics, budget):
    unique = list(dict.fromkeys(topics))
    result = demo.research(unique, budget)
    if not result["missing"]:
        reason = "complete"
    elif len(result["trace"]) < len(unique):
        reason = "budget_exhausted"
    else:
        reason = "knowledge_missing"
    result["stop_reason"] = reason
    return result

print(solve(["未知", "未知", "发票"], 2))
