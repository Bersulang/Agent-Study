# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(required, discovered):
    demo.compatible(required, discovered)
    for name, version in required.items():
        if discovered[name] != version:
            raise demo.RemoteError("工具Schema版本不兼容：" + name)
    return {"compatible": True, "tools": sorted(required)}

print(solve({"get_ticket": "1"}, {"get_ticket": "1"}))
