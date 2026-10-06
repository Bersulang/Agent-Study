"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def choose_architecture(reports, quality_floor):
    # 每个报告约定包含延迟预算；没有任何方案满足门槛则不勉强选一个。
    eligible = [item for item in reports if item["quality"] >= quality_floor and item["p95_ms"] <= item["latency_budget_ms"]]
    if not eligible:
        return "none"
    return min(eligible, key=lambda item: (item["cost"], item["name"]))["name"]

if __name__ == "__main__":
    reports = [{"name": "single", "quality": 0.5, "p95_ms": 10, "latency_budget_ms": 100, "cost": 1},
               {"name": "workflow", "quality": 1, "p95_ms": 50, "latency_budget_ms": 100, "cost": 2},
               {"name": "multi", "quality": 1, "p95_ms": 120, "latency_budget_ms": 100, "cost": 4}]
    result = choose_architecture(reports, 0.9)
    assert result == "workflow"
    assert choose_architecture(reports, 1.1) == "none"
    print(result)
