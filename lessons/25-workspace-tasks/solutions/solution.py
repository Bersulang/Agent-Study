# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

import hashlib
import tempfile

def solve(root):
    report = demo.safe_path(root, "report.json")
    signature = demo.safe_path(root, "report.sha256")
    if report.exists() and signature.exists():
        digest = hashlib.sha256(report.read_bytes()).hexdigest()
        if signature.read_text(encoding="utf-8") == digest:
            return "verified_reuse"
        raise ValueError("产物与检查点摘要不符，需要人工判断")
    demo.resume(root)
    signature.write_text(hashlib.sha256(report.read_bytes()).hexdigest(), encoding="utf-8")
    return "created"

with tempfile.TemporaryDirectory() as root:
    print(solve(root))
    print(solve(root))
