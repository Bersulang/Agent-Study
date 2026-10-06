"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def choose_evidence(evidence):
    active = [item for item in evidence if item.get("active") is True]
    if not active:
        return {"status": "no_evidence", "value": None}
    authority = max(item["authority"] for item in active)
    strongest = [item for item in active if item["authority"] == authority]
    values = {item["value"] for item in strongest}
    if len(values) != 1:
        return {"status": "conflict", "value": None}
    return {"status": "selected", "value": strongest[0]["value"]}

if __name__ == "__main__":
    evidence = [{"active": False, "authority": 99, "value": 99}, {"active": True, "authority": 2, "value": 7}]
    assert choose_evidence(evidence) == {"status": "selected", "value": 7}
    evidence.append({"active": True, "authority": 2, "value": 14})
    result = choose_evidence(evidence)
    assert result["status"] == "conflict"
    print(result)
