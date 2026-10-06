# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(evidence, budget):
    items = []
    for index, record in enumerate(evidence):
        # 明确数据边界并保留来源；包装本身不是防注入的完整保证。
        wrapped = "<evidence source=" + repr(record["source"]) + ">" + record["text"] + "</evidence>"
        items.append({"id": str(index), "priority": 1,
                      "text": wrapped, "role": "data"})
    return demo.pack(items, budget)

print(solve([{"source": "a.md", "text": "需要审批"}], 100))
