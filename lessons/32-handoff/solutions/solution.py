"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def safe_handoff(owner, target, facts, history):
    required = {"reader": "question", "ticket": "ticket_id"}
    if target not in required:
        return {"owner": owner, "status": "unknown_target", "facts": {}}
    if target in history:
        return {"owner": owner, "status": "loop_blocked", "facts": {}}
    key = required[target]
    if not facts.get(key):
        return {"owner": owner, "status": "needs_clarification", "facts": {}}
    return {"owner": target, "status": "transferred", "facts": {key: facts[key]}}

if __name__ == "__main__":
    facts = {"question": "政策", "private_note": "秘密"}
    assert safe_handoff("reception", "ticket", facts, ["reception"])["status"] == "needs_clarification"
    result = safe_handoff("reception", "reader", facts, ["reception"])
    assert result["facts"] == {"question": "政策"}
    assert facts["private_note"] == "秘密"
    print(result)
