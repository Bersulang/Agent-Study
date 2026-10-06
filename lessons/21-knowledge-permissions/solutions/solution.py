# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(query, tenant, department, documents):
    # 先按租户隔离，再交给部门过滤，两个条件必须同时成立。
    allowed = [doc for doc in documents if doc["tenant"] == tenant]
    ids = demo.search(query, department, allowed)
    return {"cache_key": (tenant, department, query), "ids": ids}

rows = [{"tenant": "A", "department": "HR", "id": "a", "text": "薪资"},
        {"tenant": "B", "department": "HR", "id": "b", "text": "薪资"}]
print(solve("薪资", "A", "HR", rows))
