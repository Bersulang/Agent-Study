"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

cache, audit = {}, []
for session, tenant in [("session-a", "A"), ("session-b", "B")]:
    api["read_ticket"](session, tenant, "T-001", cache, audit)
assert len(cache) == 2 and cache[("A", "T-001")] != cache[("B", "T-001")]
# 审批记录来自可信服务端；不能让客户端传一个approved=True获得写权限。
tickets = {("A", "T-001"): "open", ("B", "T-001"): "open"}
approval_a = {"tenant": "A", "ticket_id": "T-001", "state": "done"}
for session, tenant, approval in [("session-a", "A", None), ("session-a", "B", approval_a),
                                  ("session-b", "B", {"tenant": "B", "ticket_id": "T-001", "state": "done"})]:
    before = dict(tickets)
    try:
        api["write_ticket"](session, tenant, "T-001", "done", approval, tickets, audit)
    except PermissionError:
        assert tickets == before and audit[-1]["allowed"] is False
        print("拒绝写入：", session, tenant)
    else:
        raise AssertionError("角色或审批边界失效")
api["write_ticket"]("session-a", "A", "T-001", "done", approval_a, tickets, audit)
assert tickets[("A", "T-001")] == "done" and tickets[("B", "T-001")] == "open"
assert all("token" not in row and "content" not in row for row in audit)
print("隔离缓存：", sorted(cache)); print("最后审计：", audit[-1])
