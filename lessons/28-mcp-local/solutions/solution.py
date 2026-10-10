# 参考答案：请先独立完成exercises，再阅读本文件。
import importlib.util
from pathlib import Path

# 通过绝对文件位置载入本课演示，命令可以始终从项目根目录运行。
spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def solve(request):
    method = request.get("method") if isinstance(request, dict) else None
    if method not in {"tools/list", "tools/call"}:
        return {"ok": False, "error": {"code": "unknown_method", "message": "不支持的方法"}}
    if method == "tools/call":
        params = request.get("params")
        if not isinstance(params, dict):
            return {"ok": False, "error": {"code": "invalid_arguments", "message": "参数格式非法"}}
        if params.get("name") != "get_ticket":
            return {"ok": False, "error": {"code": "unknown_tool", "message": "未知工具"}}
        arguments = params.get("arguments")
        if not isinstance(arguments, dict) or set(arguments) != {"ticket_id"}:
            return {"ok": False, "error": {"code": "invalid_arguments", "message": "参数格式非法"}}
    try:
        return {"ok": True, "result": demo.dispatch(request)}
    except ValueError:
        # 只输出受控错误信息，不暴露文件路径或内部堆栈。
        return {"ok": False, "error": {"code": "invalid_arguments", "message": "请求未通过校验"}}

print(solve({"method": "unknown"}))
