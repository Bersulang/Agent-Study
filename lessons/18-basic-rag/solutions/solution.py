# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(questions):
    # 每个问题独立检索，避免前一个问题的证据污染后一个问题。
    rows = []
    missing = 0
    for question in questions:
        result = demo.answer(question)
        rows.append({"question": question, **result})
        if result["status"] == "no_evidence":
            missing += 1
    return {"results": rows, "missing": missing}

print(solve(["报销", "工资"]))
