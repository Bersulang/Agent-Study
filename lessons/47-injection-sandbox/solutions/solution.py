"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    root = Path(folder)
    (root / "safe.txt").write_text("合法资料", encoding="utf-8")
    (root / "config.env").write_text("不应读取", encoding="utf-8")
    (root / "nested").mkdir()
    assert api["execute_tool"](folder, "read_document", "safe.txt") == "合法资料"
    for name in ["../outside.txt", str(root / "safe.txt"), "config.env", "nested"]:
        try:
            api["resolve_read"](folder, name)
        except PermissionError:
            print("拒绝路径：", name)
        else:
            raise AssertionError("越界或非文本文件不能读取")
assert api["allowed_origin"]("https://docs.example.com/policy")
for url in ["http://docs.example.com/x", "https://user@docs.example.com/x", "https://docs.example.com:444/x"]:
    assert not api["allowed_origin"](url)
print("非法来源、用户名和端口：全部拒绝")
# DNS解析、重定向和路径检查后被替换不是本函数能解决的问题，见solutions/README.md。

def solve(data):
    """只检查本地路径和URL结构；DNS与重定向要另做真实集成验证。"""
    from pathlib import Path
    from urllib.parse import urlparse
    if data["kind"] == "file":
        root = Path(data["workspace"]).resolve()
        candidate = (root / data["path"]).resolve()
        try: candidate.relative_to(root)
        except ValueError: return {"allowed": False}
        return {"allowed": candidate.suffix.lower() in {".md", ".txt"}}
    if data["kind"] == "url":
        parsed = urlparse(data["url"])
        return {"allowed": parsed.scheme == "https" and not parsed.username and not parsed.password and parsed.port in {None, 443}}
    return {"allowed": False}
