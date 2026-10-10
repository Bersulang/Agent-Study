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


def call_read(operation, attempts=2):
    """只对只读断连有限重试；认证等其他错误原样传播。"""
    if type(attempts) is not int or attempts < 1:
        raise ValueError("尝试次数至少为1")
    for attempt in range(attempts):
        try:
            return operation()
        except ConnectionError:
            if attempt + 1 == attempts:
                raise demo.RemoteError("重连预算耗尽")

print(solve({"get_ticket": "1"}, {"get_ticket": "1"}))
