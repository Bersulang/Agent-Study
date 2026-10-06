"""一致备份与恢复演练；仅使用临时教学数据库。"""
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
from contextlib import closing

def snapshot(source, target):
    source, target = Path(source), Path(target)
    # SQLite普通connect会创建不存在的库；备份绝不能因此静默生成空库。
    if not source.is_file():
        raise FileNotFoundError("源数据库不存在")
    if target.exists() or source.resolve() == target.resolve():
        raise ValueError("备份目标须为新的隔离文件")
    # backup会读取一致快照，不对正在运行的数据库做普通文件复制。
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as src, closing(sqlite3.connect(target)) as dst:
        src.backup(dst)

def restore(backup, target):
    backup, target = Path(backup), Path(target)
    if not backup.is_file():
        raise FileNotFoundError("备份不存在")
    if target.exists() or backup.resolve() == target.resolve():
        raise ValueError("只允许恢复到新的隔离文件，禁止直接覆盖")
    # 只读打开，验证前不修改备份。
    with closing(sqlite3.connect(backup.resolve().as_uri() + "?mode=ro", uri=True)) as src:
        if src.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("备份完整性检查失败")
        # 数据库格式合法不等于业务数据正确，空库也可能返回integrity_check=ok。
        tables = {row[0] for row in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "tasks" not in tables:
            raise ValueError("备份缺少任务业务结构")
        columns = {row[1] for row in src.execute("PRAGMA table_info(tasks)")}
        if not {"id", "status"} <= columns:
            raise ValueError("备份任务Schema与应用不兼容")
        with closing(sqlite3.connect(target)) as dst:
            src.backup(dst)

def candidates(feedback):
    seen, result = set(), []
    for row in feedback:
        key = (row["category"], row["case_id"])
        if key not in seen:
            seen.add(key)
            # 仅保存脱敏标识和类别，真实案例文本另走审核流程。
            result.append({"category": key[0], "case_id": key[1], "status": "pending_review"})
    return result

if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        source, backup, target = [Path(folder) / name for name in ["source.db", "backup.db", "restored.db"]]
        with closing(sqlite3.connect(source)) as con, con:
            con.execute("CREATE TABLE tasks(id TEXT PRIMARY KEY, status TEXT)")
            con.execute("INSERT INTO tasks VALUES (?,?)", ("t1", "approved"))
        snapshot(source, backup)
        restore(backup, target)
        with closing(sqlite3.connect(target)) as con:
            print("恢复状态：", con.execute("SELECT id,status FROM tasks").fetchall())
    print("候选反馈：", candidates([{"category": "no_evidence", "case_id": "c1"}] * 2))
