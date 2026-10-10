"""参考答案：先完成练习，再比较扩展行为与错误处理。"""
import runpy
from pathlib import Path

# 复用本阶段函数，不跨阶段隐式共享状态；不会调用演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'examples/demo.py'))

from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    assistant = api["Assistant"](Path(folder) / "course.db")
    print("参数缺失：", assistant.request("lab-a", "创建工单:", "empty")["status"])
    pending = assistant.request("lab-a", "创建工单:申请帮助", "cancel")
    print("撤销：", assistant.cancel("lab-a", "cancel"))
    try:
        assistant.approve("lab-a", "cancel", pending["digest"])
    except PermissionError:
        print("撤销后写入被阻止")
    pending = assistant.request("lab-a", "创建工单:新问题", "expiry")
    try:
        assistant.approve("lab-a", "expiry", pending["digest"], now=61)
    except PermissionError:
        print("过期后写入被阻止")
    pending = assistant.request("lab-a", "创建工单:初始标题", "revise")
    revised = assistant.revise("lab-a", "revise", "修改后的标题", now=10)
    try:
        assistant.approve("lab-a", "revise", pending["digest"], now=11)
    except PermissionError:
        print("旧参数审批被拒绝")
    assistant.approve("lab-a", "revise", revised["digest"], now=11)
    print("新增只读工具：", assistant.ticket_summary("lab-a", "revise"))
    print("跨租户工具查询：", assistant.ticket_summary("lab-b", "revise"))

def solve(data):
    """检查离线审批摘要和幂等恢复规则；不代表真实重启。"""
    allowed = (data.get("approved") is True and data.get("action") == data.get("approved_action")
               and data.get("now", 0) < data.get("expires_at", 0))
    status = "unknown"
    recovered = bool(data.get("restarted", False))
    for row in data.get("operations", []):
        if row["key"] == data.get("key"):
            status = "completed" if row["digest"] == data.get("digest") else "conflict"
            break
    return {"allowed": allowed, "status": status, "recovered": recovered}
