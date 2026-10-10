"""参考答案：先完成练习，再比较扩展行为与错误处理。"""
import runpy
from pathlib import Path

# 复用本阶段函数，不跨阶段隐式共享状态；不会调用演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'examples/demo.py'))

from tempfile import TemporaryDirectory
import sqlite3
from contextlib import closing
with TemporaryDirectory() as folder:
    (Path(folder) / "calc.py").write_text(api["BEFORE"], encoding="utf-8")
    print("修复前失败测试：", api["run_check"](folder))
    try:
        api["patch"](folder, "../calc.py")
    except PermissionError:
        print("工作空间外补丁被拒绝")
    print("批准补丁：\n", api["patch"](folder, "calc.py"))
    print("实际测试：", api["run_check"](folder))
with closing(sqlite3.connect(":memory:")) as con:
    con.execute("CREATE TABLE tickets(tenant TEXT,status TEXT)")
    con.executemany("INSERT INTO tickets VALUES (?,?)", [("A", "open"), ("A", "done"), ("B", "open")])
    con.execute("PRAGMA query_only=ON")
    print("按状态报告：", api["report"](con, "A", "by_status"))
    try:
        api["report"](con, "A", "DELETE FROM tickets")
    except PermissionError:
        print("任意SQL报告被拒绝")

def solve(data):
    """确认补丁路径处于工作区内，并让过期审查与失败测试保持未修复。"""
    from pathlib import Path
    root = Path(data["workspace"]).resolve()
    candidate = (Path(data["path"])).resolve() if Path(data["path"]).is_absolute() else (Path.cwd() / data["path"]).resolve()
    try: candidate.relative_to(root)
    except ValueError: return {"allowed": False, "stale": data.get("current") != data.get("reviewed"), "diff": None, "status": "blocked"}
    stale = data.get("current") != data.get("reviewed")
    passed = data.get("tests_passed", True)
    status = "fixed" if passed and not stale else "pending"
    return {"allowed": True, "stale": stale, "diff": {"before": data.get("reviewed"), "after": data.get("current")}, "status": status}
