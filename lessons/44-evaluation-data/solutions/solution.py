"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

cases = api["CASES"] + [{"id": "partial-1", "category": "incomplete", "expected": "clarify"}]
predictions = [{"id": row["id"], "action": row["expected"]} for row in cases]
report = api["evaluate"](cases, predictions)
assert report["success_rate"] == 1 and "incomplete" in report["by_category"]
print("最差类别：", min(report["by_category"], key=report["by_category"].get))
# 安全失败即使总体达标也必须拒绝；类别门槛另外保护少数失败类别。
unsafe = {"success_rate": .99, "security_violations": ["unsafe-1"], "by_category": {"normal": 1, "security": 0}}
assert not api["release_decision"](unsafe)
weak = {"success_rate": .95, "security_violations": [], "by_category": {"normal": 1, "incomplete": 0}}
assert not api["release_decision"](weak)
for rows in [predictions[:-1], predictions + [predictions[0]]]:
    try:
        api["evaluate"](cases, rows)
    except ValueError:
        print("缺失或重复预测：拒绝")
    else:
        raise AssertionError("非法预测不应参与计算")
assert api["disagreements"]({"q1": True}, {"q1": False}) == ["q1"]
print("人工与模型评分分歧：q1需复核；发布：", api["release_decision"](report))

def solve(data):
    """独立评估适配器：保证预测一一对应并单独阻断安全违规。"""
    cases, predictions = data["cases"], data["predictions"]
    expected_ids = [row["id"] for row in cases]
    actual_ids = [row["id"] for row in predictions]
    if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != set(expected_ids):
        raise ValueError("预测必须与评估集一一对应")
    by_id = {row["id"]: row for row in predictions}
    category_scores = {}
    all_scores = []
    for case in cases:
        prediction = by_id[case["id"]]
        score = float(prediction.get("action") == case["expected"])
        all_scores.append(score)
        category_scores.setdefault(case["category"], []).append(score)
    by_category = {name: sum(scores) / len(scores) for name, scores in category_scores.items()}
    success_rate = sum(all_scores) / len(all_scores) if all_scores else 1.0
    safe = not any(row.get("security_violation") for row in predictions)
    return {"success_rate": success_rate, "by_category": by_category,
            "release": safe and success_rate >= data["threshold"]}
