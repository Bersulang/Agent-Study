# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(index, rows):
    # 临时对象承载构建结果；验证成功之前绝不触碰读入口。
    candidate = demo.Index()
    for identity, text in rows:
        candidate.update(identity, text)
    index.documents = candidate.documents
    index.generation += 1
    return index.generation

index = demo.Index()
index.update("old", "旧政策")
print(solve(index, [("new", "新政策")]), index.documents)
