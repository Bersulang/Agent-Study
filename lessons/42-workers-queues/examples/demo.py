"""SQLite 本地租约队列：唯一投递键、原子领取、fencing token拒绝旧Worker。"""
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

class Queue:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, state TEXT, owner TEXT, expires REAL, token INTEGER);
            CREATE TABLE IF NOT EXISTS effects(job_id TEXT PRIMARY KEY);
        """)

    def enqueue(self, job_id):
        self.db.execute("INSERT OR IGNORE INTO jobs VALUES (?, 'pending', NULL, 0, 0)", (job_id,))

    def claim(self, job_id, owner, now, ttl=10):
        # 显式写事务串行化领取，不能先SELECT再在事务外UPDATE。
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT state,expires,token FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None or row[0] == "done" or (row[0] == "leased" and row[1] > now):
                self.db.execute("COMMIT")
                return None
            token = row[2] + 1
            self.db.execute("UPDATE jobs SET state='leased',owner=?,expires=?,token=? WHERE id=?",
                            (owner, now + ttl, token, job_id))
            self.db.execute("COMMIT")
            return token
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def complete(self, job_id, owner, token, now):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            updated = self.db.execute("UPDATE jobs SET state='done' WHERE id=? AND owner=? AND token=? AND state='leased' AND expires>?",
                                      (job_id, owner, token, now))
            accepted = updated.rowcount == 1
            if accepted:
                # 示例副作用在同一数据库事务中；外部HTTP必须另做幂等。
                self.db.execute("INSERT OR IGNORE INTO effects VALUES (?)", (job_id,))
            self.db.execute("COMMIT")
            return accepted
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def close(self):
        self.db.close()

def run_case(case):
    with TemporaryDirectory() as folder:
        path = Path(folder) / "queue.db"
        api = Queue(path)
        worker = Queue(path)  # 第二条真实连接，不共享Python对象。
        try:
            api.enqueue("T-7")
            api.enqueue("T-7")
            first = worker.claim("T-7", "worker-a", now=100)
            if case == "busy":
                return {"second_claim": api.claim("T-7", "worker-b", now=101), "status": "leased"}
            if case == "lease":
                second = api.claim("T-7", "worker-b", now=111)
                stale = worker.complete("T-7", "worker-a", first, now=112)
                api.complete("T-7", "worker-b", second, now=112)
                effects = api.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
                return {"first_token": first, "second_token": second, "stale_accepted": stale, "effects": effects}
            worker.complete("T-7", "worker-a", first, now=101)
            worker.complete("T-7", "worker-a", first, now=102)
            return {"jobs": api.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
                    "effects": api.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0], "status": "done"}
        finally:
            worker.close()
            api.close()

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['duplicate', 'lease', 'busy']:
        print(case, run_case(case))
