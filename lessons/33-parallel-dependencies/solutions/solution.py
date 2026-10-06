"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def dependency_summary(knowledge, ticket):
    # None是缺失，空字符串是已返回但无内容，单独列入empty。
    inputs = {"knowledge": knowledge, "ticket": ticket}
    missing = [name for name, value in inputs.items() if value is None or value == "timeout"]
    empty = [name for name, value in inputs.items() if value == ""]
    if missing or empty:
        return {"status": "blocked", "missing": missing, "empty": empty, "summary": None}
    return {"status": "completed", "missing": [], "empty": [], "summary": f"{knowledge} / {ticket}"}

if __name__ == "__main__":
    assert dependency_summary("policy-v2", "timeout")["missing"] == ["ticket"]
    assert dependency_summary("", "T-7")["empty"] == ["knowledge"]
    result = dependency_summary("policy-v2", "T-7")
    assert result["summary"] == "policy-v2 / T-7"
    print(result)
