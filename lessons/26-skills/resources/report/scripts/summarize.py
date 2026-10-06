"""能力包的只读处理脚本：先校验记录再统计，不修改原工单。"""
import json
from pathlib import Path
import argparse


def summarize(rows):
    counts = {"open": 0, "closed": 0}
    seen, errors = set(), []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            errors.append({"row": index, "reason": "missing_id"})
            continue
        if row.get("status") not in counts:
            errors.append({"row": index, "id": row["id"], "reason": "invalid_status"})
            continue
        if row["id"] in seen:
            continue
        # 校验成功后才把id记为已处理，避免无效记录压掉后面的有效记录。
        seen.add(row["id"])
        counts[row["status"]] += 1
    return {"counts": counts, "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="统计调用方已授权的工单列表，不提供认证功能")
    parser.add_argument("file", nargs="?", help="UTF-8 JSON列表；不填时运行离线夹具")
    args = parser.parse_args()
    rows = json.loads(Path(args.file).read_text(encoding="utf-8")) if args.file else [
        {"id": "T1", "status": "open"}, {"id": "T1", "status": "open"},
        {"id": "T2", "status": "closed"}, {"id": "T3"}]
    if not isinstance(rows, list):
        raise ValueError("输入必须是JSON列表")
    print(json.dumps(summarize(rows), ensure_ascii=False))
