# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(rankings):
    scores = {}
    for ranking in rankings:
        # 同一检索器的重复id不应额外获得分数。
        seen = set()
        for rank, identity in enumerate(ranking, 1):
            if identity in seen:
                continue
            seen.add(identity)
            scores[identity] = scores.get(identity, 0) + 1 / (60 + rank)
    return sorted(scores, key=lambda identity: (-scores[identity], identity))

print(solve([["A", "B"], ["B", "C"]]))
