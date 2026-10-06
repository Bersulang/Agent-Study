"""离线研究流程：资料和结论都是教学夹具，不是实际企业政策。"""
from concurrent.futures import ThreadPoolExecutor

SOURCES = {
    "policy-a": {"id": "policy-a", "active": True, "facts": {"reply_hours": 24}},
    "policy-b": {"id": "policy-b", "active": True, "facts": {"reply_hours": 48}},
    "old-policy": {"id": "old-policy", "active": False, "facts": {"reply_hours": 72}},
}

def retrieve(source_id):
    if source_id not in SOURCES:
        raise ValueError("来源不存在")
    source = SOURCES[source_id]
    return source if source["active"] else None

def research(source_ids, budget=3):
    ids = sorted(set(source_ids))
    if not ids or len(ids) > budget:
        raise ValueError("没有来源或研究超出预算")
    # 线程池数量有限；真实检索还需每调用超时与网络限制。
    with ThreadPoolExecutor(max_workers=2) as pool:
        evidence = [row for row in pool.map(retrieve, ids) if row is not None]
    claims = {}
    for source in evidence:
        for key, value in source["facts"].items():
            claims.setdefault(key, []).append({"value": value, "source": source["id"]})
    conflicts = [key for key, rows in claims.items() if len({row["value"] for row in rows}) > 1]
    return {"status": "needs_review" if conflicts else "ready" if claims else "no_evidence",
            "claims": claims, "conflicts": conflicts}

def report(result):
    if result["status"] != "ready":
        return "证据不足或存在冲突，不生成确定结论"
    return "\n".join(f"{key}={rows[0]['value']}；来源：{','.join(row['source'] for row in rows)}"
                     for key, rows in sorted(result["claims"].items()))

if __name__ == "__main__":
    print("单来源报告：", report(research(["policy-a"])))
    conflict = research(["policy-a", "policy-b"])
    print("冲突状态：", conflict["status"], conflict["conflicts"])
    print("过期资料：", research(["old-policy"])["status"])
