"""审批绑定动作摘要；幂等结果和副作用在同一个SQLite事务提交。"""
import hashlib
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

def digest(action):
    # 固定key排序和分隔符，避免JSON空格变化导致同一动作摘要不同。
    raw = json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY, digest TEXT, expires REAL, revoked INTEGER);
            CREATE TABLE IF NOT EXISTS operations(key TEXT PRIMARY KEY, digest TEXT, result TEXT);
            CREATE TABLE IF NOT EXISTS effects(ticket_id TEXT PRIMARY KEY, state TEXT);
        """)

    def approve(self, approval_id, action, expires):
        with self.db:
            self.db.execute("INSERT INTO approvals VALUES (?, ?, ?, 0)", (approval_id, digest(action), expires))

    def revoke(self, approval_id):
        with self.db:
            self.db.execute("UPDATE approvals SET revoked=1 WHERE id=?", (approval_id,))

    def execute(self, key, approval_id, action, now):
        # 提交前独占写锁，两个连接不能同时认为相同key不存在。
        self.db.execute("BEGIN IMMEDIATE")
        try:
            action_digest = digest(action)
            saved = self.db.execute("SELECT digest,result FROM operations WHERE key=?", (key,)).fetchone()
            if saved:
                if saved[0] != action_digest:
                    raise ValueError("idempotency_key_conflict")
                self.db.commit()
                return saved[1], True  # 仅查证已完成结果，不再次使用审批执行。
            approval = self.db.execute("SELECT digest,expires,revoked FROM approvals WHERE id=?", (approval_id,)).fetchone()
            if approval is None or approval[0] != action_digest:
                raise ValueError("approval_mismatch")
            if approval[2]:
                raise ValueError("approval_revoked")
            if now >= approval[1]:
                raise ValueError("approval_expired")
            if action.get("kind") != "close" or set(action) != {"kind", "ticket_id"}:
                raise ValueError("invalid_action")
            result = "closed:" + action["ticket_id"]
            self.db.execute("INSERT INTO effects VALUES (?, 'closed')", (action["ticket_id"],))
            self.db.execute("INSERT INTO operations VALUES (?, ?, ?)", (key, action_digest, result))
            self.db.commit()
            return result, False
        except BaseException:
            self.db.rollback()
            raise

    def close(self):
        self.db.close()

def run_case(case):
    with TemporaryDirectory() as folder:
        path = Path(folder) / "ledger.db"
        ledger = Ledger(path)
        action = {"kind": "close", "ticket_id": "T-7"}
        ledger.approve("approval-7", action, expires=200)
        try:
            if case == "revoked":
                ledger.revoke("approval-7")
            if case == "changed":
                action["ticket_id"] = "T-8"
            try:
                result, replayed = ledger.execute("operation-7", "approval-7", action, now=200 if case == "expired" else 100)
            except ValueError as exc:
                return {"effects": ledger.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0], "error": str(exc)}
        finally:
            ledger.close()
        # 模拟业务已提交但HTTP响应丢失：重启连接后携带同一key查证。
        recovered = Ledger(path)
        try:
            result, replayed = recovered.execute("operation-7", "approval-7", action, now=300)
            return {"effects": recovered.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0],
                    "result": result, "replayed": replayed}
        finally:
            recovered.close()

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['replay', 'expired', 'changed', 'revoked']:
        print(case, run_case(case))
