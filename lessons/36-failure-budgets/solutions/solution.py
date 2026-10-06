"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def allocate_budget(total, task_names):
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("预算必须是非负整数")
    if len(set(task_names)) != len(task_names):
        raise ValueError("任务名不能重复")
    if not task_names:
        if total:
            raise ValueError("正预算必须有接收任务")
        return {}
    base, remainder = divmod(total, len(task_names))
    return {name: base + (index < remainder) for index, name in enumerate(task_names)}

if __name__ == "__main__":
    result = allocate_budget(5, ["policy", "ticket", "review"])
    assert result == {"policy": 2, "ticket": 2, "review": 1}
    assert sum(result.values()) == 5
    assert allocate_budget(0, []) == {}
    print(result)
