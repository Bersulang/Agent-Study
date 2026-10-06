# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(request):
    try:
        return {"ok": True, "result": demo.dispatch(request)}
    except ValueError as error:
        # 只输出受控错误信息，不暴露文件路径或内部堆栈。
        return {"ok": False, "error": {"code": "INVALID_REQUEST", "message": str(error)}}

print(solve({"method": "unknown"}))
