"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def batch_route(requests, allowed_roles):
    routes = []
    counts = {"knowledge": 0, "ticket": 0, "human": 0}
    for text in requests:
        result = demo.route(text.strip(), allowed_roles)
        routes.append(result)
        counts[result["role"]] += 1
    return {"routes": routes, "counts": counts}

if __name__ == "__main__":
    requests = ["政策", "工单", "  ", "政策和工单"]
    result = batch_route(requests, {"knowledge", "ticket"})
    assert result["counts"] == {"knowledge": 1, "ticket": 1, "human": 2}
    assert requests[2] == "  "  # 不能原地改写调用者输入。
    print(result)
