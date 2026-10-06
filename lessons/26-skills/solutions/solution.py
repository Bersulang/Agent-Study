# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(name, permissions, expected_version):
    meta = demo.load(name, permissions)
    if meta["version"] != expected_version:
        raise ValueError("能力包版本变化，需重新检查兼容性")
    return meta

print(solve("report", {"read"}, "1.0"))
