"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

events = []
# 同一个请求的两个步骤关联同一ID；失败异常会传播，但类型留在轨迹中。
with api["span"](events, "request-002", "model"):
    result = {"content": "不记录业务正文"}
try:
    with api["span"](events, "request-002", "tool"):
        raise TimeoutError("敏感正文不应出现在日志")
except TimeoutError:
    pass
assert {row["request_id"] for row in events} == {"request-002"}
assert events[-1]["error_type"] == "TimeoutError"
assert "敏感正文" not in str(events)
print("关联步骤：", [(row["span"], row["status"], row["error_type"]) for row in events])
print("嵌套脱敏：", api["redact"]({"user": "mason@example.com", "nested": [{"token": "secret"}]}))
assert api["estimate_cost"](1000, 200, 1, 2) == .0014
for values in [(-1, 1, 1, 1), (1, 1, -1, 1)]:
    try:
        api["estimate_cost"](*values)
    except ValueError:
        print("负数用量或价格：拒绝")
    else:
        raise AssertionError("负数不能计价")
print("假设成本：", api["estimate_cost"](1000, 200, 1, 2))

def solve(data):
    """生成脱敏的请求摘要并计算非负用量成本。"""
    input_tokens, output_tokens = data["input_tokens"], data["output_tokens"]
    if type(input_tokens) is not int or type(output_tokens) is not int or min(input_tokens, output_tokens) < 0:
        raise ValueError("token数量必须是非负整数")
    error = data.get("error") or {}
    return {"request_id": data["request_id"], "error_type": error.get("type"),
            "cost": input_tokens / 1_000_000 + output_tokens * 2 / 1_000_000}
