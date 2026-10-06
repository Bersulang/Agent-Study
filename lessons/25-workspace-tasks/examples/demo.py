# 工作空间与任务恢复：默认标准库、离线、有限退出。
from pathlib import Path
import json
import tempfile

def safe_path(root, relative):
    base = Path(root).resolve()
    target = (base / relative).resolve()
    # resolve处理..与已有符号链接，但不能消除并发换链接的竞争风险。
    if not target.is_relative_to(base):
        raise PermissionError("路径越过工作空间")
    return target

def resume(root):
    checkpoint = safe_path(root, "checkpoint.json")
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text(encoding="utf-8"))
    else:
        state = {"stage": "new"}
    report = safe_path(root, "report.json")
    if state["stage"] == "done" and report.exists():
        return "reused"
    report.write_text(json.dumps({"summary": "工单统计完成"}, ensure_ascii=False), encoding="utf-8")
    # 先写产物再标记完成；否则恢复可能误以为未写出的产物已存在。
    checkpoint.write_text(json.dumps({"stage": "done"}), encoding="utf-8")
    return "created"

def main():
    with tempfile.TemporaryDirectory() as root:
        print(resume(root))
        print(resume(root))

if __name__ == "__main__":
    main()
