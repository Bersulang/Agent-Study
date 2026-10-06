"""毕业参考基线：模型和身份为离线夹具，其余本地持久行为实际执行。"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sqlite3

SESSIONS = {
    "lab-a": {"tenant": "A", "roles": {"read", "write", "approve"}},
    "lab-b": {"tenant": "B", "roles": {"read", "write", "approve"}},
    "lab-reader": {"tenant": "A", "roles": {"read"}},
}

def principal(token, capability):
    identity = SESSIONS.get(token)
    if identity is None or capability not in identity["roles"]:
        raise PermissionError("身份或能力未授权")
    return identity

def fixture_plan(question):
    # 确定性规划夹具，只覆盖明确案例；真实模型替换这里但不能扩展权限。
    if question.startswith("创建工单:"):
        title = question.split(":", 1)[1].strip()
        return {"action": "draft", "title": title}
    return {"action": "answer", "query": question}

def proposal_hash(tenant, title):
    payload = {"tenant": tenant, "action": "create_ticket", "title": title, "version": "v1"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

class Assistant:
    def __init__(self, database, planner=fixture_plan):
        self.database, self.planner = str(database), planner
        with closing(sqlite3.connect(self.database)) as con, con:
            con.execute("CREATE TABLE IF NOT EXISTS drafts(tenant TEXT,key TEXT,title TEXT,digest TEXT,status TEXT,expires REAL,ticket INTEGER,PRIMARY KEY(tenant,key))")
            con.execute("CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,tenant TEXT,key TEXT,title TEXT,UNIQUE(tenant,key))")

    def answer(self, tenant, query):
        def knowledge_worker():
            # 明确标注的教学知识，不等同真实RAG与企业政策。
            return {"text": "教学政策：7天内可提交申请", "source": "fixture-policy-A"} if tenant == "A" and "政策" in query else None

        def business_worker():
            with closing(sqlite3.connect(self.database)) as con:
                return con.execute("SELECT COUNT(*) FROM tickets WHERE tenant=?", (tenant,)).fetchone()[0]

        with ThreadPoolExecutor(max_workers=2) as pool:
            knowledge_future = pool.submit(knowledge_worker)
            count_future = pool.submit(business_worker)
            evidence, count = knowledge_future.result(), count_future.result()
        return {"status": "answered" if evidence else "no_evidence", "evidence": evidence,
                "ticket_count": count, "trace": ["authenticated", "knowledge", "business", "finished"]}

    def request(self, token, question, key, now=0.0):
        identity = principal(token, "read")
        if not isinstance(question, str) or not question or not isinstance(key, str) or not 1 <= len(key) <= 64:
            raise ValueError("问题或幂等键不合法")
        plan = self.planner(question)
        if not isinstance(plan, dict) or plan.get("action") not in {"answer", "draft"}:
            raise PermissionError("规划提出了未授权动作")
        if plan["action"] == "answer":
            return self.answer(identity["tenant"], plan.get("query", question))
        principal(token, "write")
        title = plan.get("title")
        if not isinstance(title, str) or not title.strip():
            return {"status": "clarify", "missing": "title"}
        if len(title) > 200:
            raise ValueError("标题超过限制")
        tenant, digest = identity["tenant"], proposal_hash(identity["tenant"], title)
        with closing(sqlite3.connect(self.database)) as con, con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT digest,status,ticket FROM drafts WHERE tenant=? AND key=?", (tenant, key)).fetchone()
            if row:
                if row[0] != digest:
                    raise ValueError("同一幂等键不能绑定不同参数")
                return {"status": row[1], "digest": row[0], "ticket": row[2]}
            con.execute("INSERT INTO drafts VALUES (?,?,?,?,?,?,?)", (tenant, key, title, digest, "pending", now + 60, None))
        return {"status": "pending", "digest": digest, "ticket": None}

    def approve(self, token, key, expected_digest, now=1.0):
        identity = principal(token, "approve")
        tenant = identity["tenant"]
        with closing(sqlite3.connect(self.database)) as con, con:
            # 单事务绑定查状态、写工单与更新任务，串行化本地竞争审批。
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT title,digest,status,expires,ticket FROM drafts WHERE tenant=? AND key=?", (tenant, key)).fetchone()
            if row is None:
                raise PermissionError("任务不存在或不属于当前租户")
            title, digest, status, expires, ticket = row
            if expected_digest != digest or proposal_hash(tenant, title) != digest:
                raise PermissionError("批准参数已改变")
            if status == "done":
                return {"status": "done", "ticket": ticket}
            if status != "pending" or now >= expires:
                raise PermissionError("审批已撤销、失效或过期")
            ticket = con.execute("INSERT INTO tickets(tenant,key,title) VALUES (?,?,?)", (tenant, key, title)).lastrowid
            con.execute("UPDATE drafts SET status='done',ticket=? WHERE tenant=? AND key=?", (ticket, tenant, key))
            return {"status": "done", "ticket": ticket}

    def revise(self, token, key, title, now=1.0):
        """明确编辑草稿并重置批准绑定，不复用旧批准。"""
        identity = principal(token, "write")
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError("新标题不合法")
        tenant, digest = identity["tenant"], proposal_hash(identity["tenant"], title)
        with closing(sqlite3.connect(self.database)) as con, con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT status FROM drafts WHERE tenant=? AND key=?", (tenant, key)).fetchone()
            if row is None or row[0] != "pending":
                raise PermissionError("只能编辑当前租户的待审批草稿")
            con.execute("UPDATE drafts SET title=?,digest=?,expires=? WHERE tenant=? AND key=?",
                        (title, digest, now + 60, tenant, key))
        return {"status": "pending", "digest": digest, "ticket": None}

    def ticket_summary(self, token, key):
        """新增只读业务工具：查询必须绑定认证租户，而非请求自报租户。"""
        identity = principal(token, "read")
        with closing(sqlite3.connect(self.database)) as con:
            row = con.execute("SELECT id,title FROM tickets WHERE tenant=? AND key=?", (identity["tenant"], key)).fetchone()
        return {"id": row[0], "title": row[1]} if row else None

    def cancel(self, token, key):
        identity = principal(token, "write")
        with closing(sqlite3.connect(self.database)) as con, con:
            changed = con.execute("UPDATE drafts SET status='cancelled' WHERE tenant=? AND key=? AND status='pending'", (identity["tenant"], key)).rowcount
        return {"cancelled": changed == 1}

if __name__ == "__main__":
    with TemporaryDirectory() as folder:
        database = Path(folder) / "assistant.db"
        assistant = Assistant(database)
        print("知识与业务：", assistant.request("lab-a", "查询政策", "q1")["status"])
        pending = assistant.request("lab-a", "创建工单:登录失败", "k1")
        print("创建前：", pending["status"])
        created = assistant.approve("lab-a", "k1", pending["digest"])
        restored = Assistant(database)
        print("重启重放：", restored.approve("lab-a", "k1", pending["digest"]) == created)
        try:
            restored.approve("lab-b", "k1", pending["digest"])
        except PermissionError as error:
            print("租户边界：", error)
