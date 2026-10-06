"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def classify_http_error(status):
    known = {401: "authentication", 403: "authorization", 404: "not_found", 429: "retryable_read", 503: "retryable_read"}
    return known.get(status, "permanent")

if __name__ == "__main__":
    cases = {401: "authentication", 403: "authorization", 404: "not_found", 429: "retryable_read", 503: "retryable_read", 400: "permanent"}
    for status, expected in cases.items():
        assert classify_http_error(status) == expected
    print({status: classify_http_error(status) for status in cases})
