"""参考答案：先完成练习，再比较扩展行为与错误处理。"""
import runpy
from pathlib import Path

# 复用本阶段函数，不跨阶段隐式共享状态；不会调用演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'examples/demo.py'))

import sqlite3
from tempfile import TemporaryDirectory
from contextlib import closing
with TemporaryDirectory() as folder:
    source, backup, target = [Path(folder) / name for name in ["s.db", "b.db", "r.db"]]
    with closing(sqlite3.connect(source)) as con, con:
        con.execute("CREATE TABLE tasks(id TEXT PRIMARY KEY,status TEXT)")
        con.executemany("INSERT INTO tasks VALUES (?,?)", [("1", "done"), ("2", "pending")])
    api["snapshot"](source, backup)
    api["restore"](backup, target)
    with closing(sqlite3.connect(target)) as con:
        print("恢复数量：", con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])
        print("恢复状态：", con.execute("SELECT id,status FROM tasks ORDER BY id").fetchall())
    # 缺失和损坏备份不得创建目标，更不能覆盖运行中的数据库。
    for backup_path in [Path(folder) / "missing.db", Path(folder) / "broken.db"]:
        if backup_path.name == "broken.db":
            backup_path.write_bytes(b"not a database")
        try:
            api["restore"](backup_path, Path(folder) / "failure-target.db")
        except (FileNotFoundError, sqlite3.DatabaseError, ValueError) as error:
            print("恢复失败分类：", type(error).__name__)
    try:
        api["snapshot"](Path(folder) / "missing-source.db", Path(folder) / "empty.db")
    except FileNotFoundError:
        print("缺失源数据库不会静默创建空备份")
print("候选不会自动发布：", api["candidates"]([{"category": "failure", "case_id": "c2"}]))
