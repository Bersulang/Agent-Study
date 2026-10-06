"""本地结构化追踪教具；价格仅是假设值，不是供应商报价。"""
from contextlib import contextmanager
from time import perf_counter
import re

SENSITIVE = {"authorization", "api_key", "token", "password", "content"}

def redact(value):
    """递归脱敏；正文默认不记录，文本模式仅做补充。"""
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in SENSITIVE else redact(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", value)
    return value

@contextmanager
def span(events, request_id, name):
    start, status, error_type = perf_counter(), "ok", None
    try:
        yield
    except Exception as error:
        # 不记录原始异常文本，避免工具错误中混入敏感内容。
        status = "error"
        error_type = type(error).__name__
        raise
    finally:
        events.append({"request_id": request_id, "span": name, "status": status, "error_type": error_type,
                       "duration_ms": round((perf_counter() - start) * 1000, 3)})

def estimate_cost(input_tokens, output_tokens, input_per_million, output_per_million):
    if min(input_tokens, output_tokens, input_per_million, output_per_million) < 0:
        raise ValueError("用量和单价不能为负")
    return (input_tokens * input_per_million + output_tokens * output_per_million) / 1_000_000

if __name__ == "__main__":
    events = []
    with span(events, "request-001", "lookup"):
        result = {"count": 2, "credentials": {"api_key": "demo-secret"}}
    print("轨迹：", [{key: value for key, value in event.items() if key != "duration_ms"} for event in events])
    print("脱敏结果：", redact(result))
    print("假设成本：", estimate_cost(1000, 200, 1, 2))
