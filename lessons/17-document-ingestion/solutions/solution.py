# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(items):
    # 正文作为键去重；来源是列表，不能因为去重丢失引用。
    unique, errors = {}, []
    for source, text in items:
        try:
            for chunk in demo.ingest(text, source):
                key = chunk["text"]
                if key not in unique:
                    unique[key] = {"text": key, "locations": []}
                unique[key]["locations"].append((source, chunk["paragraph"]))
        except ValueError as error:
            errors.append({"source": source, "error": str(error)})
    return {"chunks": list(unique.values()), "errors": errors}

print(solve([("a.md", "需要发票"), ("b.md", "需要发票"), ("scan.pdf", "")]))
