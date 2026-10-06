# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(memory, user, key, value, source, expires, consent, now):
    if not consent:
        raise PermissionError("没有修正授权")
    old = memory.get(user, key, now)
    memory.put(user, key, value, source, expires, consent)
    return {"user": user, "key": key, "old": old, "new": value, "source": source}

memory = demo.Memory()
print(solve(memory, "u", "language", "中文", "m1", 20, True, 1))
print(solve(memory, "u", "language", "英文", "m2", 20, True, 2))
