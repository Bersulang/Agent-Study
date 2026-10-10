"""参考答案：先完成练习，再比较扩展行为与错误处理。"""
import runpy
from pathlib import Path

# 复用本阶段函数，不跨阶段隐式共享状态；不会调用演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'examples/demo.py'))

page = api["PageTask"]()
try:
    page.submit(False)
except PermissionError:
    print("未审批提交被拒绝")
first = page.submit(True)
assert page.state == "confirmed"
assert page.submit(True) == first
print("后置条件与去重：", first)
for mime, size in [("image/png", 0), ("application/executable", 10), ("audio/wav", 2_000_000)]:
    try:
        api["check_media"](mime, size)
    except ValueError:
        print("拒绝输入：", mime, size)

_UPLOADS = {}

def solve(data):
    """校验离线上传规则，并在相同键和内容重试时复用工单号。"""
    import hashlib
    content = data.get("content", "")
    maximum = data.get("max_chars", 4096)
    if (not data.get("approved") or data.get("mime") not in {"text/plain", "text/markdown", "application/pdf"}
            or not content or len(content) > maximum):
        return {"accepted": False, "ticket_id": None, "replayed": False}
    key = data["key"]
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    prior = _UPLOADS.get(key)
    if prior is not None:
        if prior[0] != digest: return {"accepted": False, "ticket_id": None, "replayed": False, "status": "conflict"}
        return {"accepted": True, "ticket_id": prior[1], "replayed": True}
    ticket_id = f"T-{len(_UPLOADS) + 1}"
    _UPLOADS[key] = (digest, ticket_id)
    return {"accepted": True, "ticket_id": ticket_id, "replayed": False}
