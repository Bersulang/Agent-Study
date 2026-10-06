"""受控补丁和只读报告；不执行任意模型代码，不是OS沙箱。"""
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import closing
import difflib
import sqlite3
import subprocess
import sys

BEFORE = "def add(a, b):\n    return a - b\n"
AFTER = "def add(a, b):\n    return a + b\n"

def patch(root, relative):
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if target.parent != root or target.name != "calc.py":
        raise PermissionError("仅允许批准的calc.py")
    previous = target.read_text(encoding="utf-8")
    if previous != BEFORE:
        raise ValueError("旧内容与批准补丁不匹配")
    target.write_text(AFTER, encoding="utf-8")
    return "".join(difflib.unified_diff(previous.splitlines(True), AFTER.splitlines(True), fromfile="before", tofile="after"))

def run_check(root):
    # 只执行我们编写的固定测试，列表参数避免shell解释；超时限制不是沙箱。
    command = [sys.executable, "-I", "-c", "import runpy; x=runpy.run_path('calc.py'); assert x['add'](2,3)==5"]
    result = subprocess.run(command, cwd=root, capture_output=True, timeout=3)
    return {"passed": result.returncode == 0, "exit_code": result.returncode}

def report(connection, tenant, kind):
    queries = {
        "count": "SELECT COUNT(*) FROM tickets WHERE tenant=?",
        "by_status": "SELECT status,COUNT(*) FROM tickets WHERE tenant=? GROUP BY status LIMIT 100",
    }
    if kind not in queries:
        raise PermissionError("只允许预定义报告")
    return connection.execute(queries[kind], (tenant,)).fetchall()

if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        (Path(folder) / "calc.py").write_text(BEFORE, encoding="utf-8")
        print("修复前：", run_check(folder))
        patch(folder, "calc.py")
        print("修复后：", run_check(folder))
    with closing(sqlite3.connect(":memory:")) as con:
        con.execute("CREATE TABLE tickets(tenant TEXT,status TEXT)")
        con.executemany("INSERT INTO tickets VALUES (?,?)", [("A", "open"), ("B", "done")])
        # 数据库级query_only作为模板白名单之外的第二道边界。
        con.execute("PRAGMA query_only=ON")
        print("A只读报告：", report(con, "A", "count"))
