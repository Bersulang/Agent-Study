"""参考答案：先完成练习，再比较扩展行为与错误处理。"""
import runpy
from pathlib import Path

# 复用本阶段函数，不跨阶段隐式共享状态；不会调用演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'examples/demo.py'))

# 去重与过期过滤，重复来源不会伪装成多份独立证据。
result = api["research"](["policy-a", "policy-a", "old-policy"])
print(api["report"](result))
conflict = api["research"](["policy-a", "policy-b"])
print("冲突不得生成确定报告：", api["report"](conflict))
print("证据表：", result["claims"])
try:
    api["research"](["missing-source"])
except ValueError:
    print("缺失来源不能充当证据")

def solve(data):
    """过滤过期事实，要求来源并按来源标识稳定去重。"""
    facts, seen = [], set()
    for row in data["facts"]:
        if not row.get("active", False): continue
        source = row.get("source")
        if not isinstance(source, str) or not source.strip(): raise ValueError("事实缺少来源")
        if source in seen: continue
        seen.add(source)
        facts.append({"text": row["text"], "source": source})
    return {"facts": facts}
