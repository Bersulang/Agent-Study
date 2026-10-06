"""持久化检查点：业务状态和审计一起提交，冲突及异常均回滚。"""
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, state TEXT NOT NULL, version INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(task_id TEXT NOT NULL, event TEXT NOT NULL);
        """)

    def create(self, task_id):
        with self.db:
            self.db.execute("INSERT INTO tasks VALUES (?, 'new', 0)", (task_id,))

    def save(self, task_id, state, expected_version, crash=False):
        with self.db:
            updated = self.db.execute("UPDATE tasks SET state=?, version=version+1 WHERE id=? AND version=?",
                                      (state, task_id, expected_version))
            if updated.rowcount != 1:
                raise ValueError("version_conflict")
            if crash:
                raise RuntimeError("模拟提交前故障")
            self.db.execute("INSERT INTO audit VALUES (?, ?)", (task_id, "checkpoint_saved"))

    def load(self, task_id):
        state, version = self.db.execute("SELECT state,version FROM tasks WHERE id=?", (task_id,)).fetchone()
        audit = self.db.execute("SELECT COUNT(*) FROM audit WHERE task_id=?", (task_id,)).fetchone()[0]
        return {"state": state, "version": version, "audit": audit}

    def close(self):
        self.db.close()  # 连接上下文只负责事务，不自动关闭连接。

def run_case(case):
    with TemporaryDirectory() as folder:
        path = Path(folder) / "tasks.db"
        store = Store(path)
        try:
            store.create("T-7")
            error = None
            try:
                store.save("T-7", "ready", 0, crash=case == "rollback")
                if case == "conflict":
                    store.save("T-7", "blocked", 0)
            except RuntimeError:
                pass
            except ValueError as exc:
                error = str(exc)
        finally:
            store.close()
        # 新连接读取，证明结果来自磁盘，而非原对象还在内存。
        recovered = Store(path)
        try:
            result = recovered.load("T-7")
        finally:
            recovered.close()
        if error:
            result.pop("audit")
            result["error"] = error
        return result

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['restart', 'rollback', 'conflict']:
        print(case, run_case(case))
