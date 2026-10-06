"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def query_operation(ledger, key, action):
    saved = ledger.db.execute("SELECT digest,result FROM operations WHERE key=?", (key,)).fetchone()
    if saved is None:
        return {"status": "unknown", "result": None}
    if saved[0] != demo.digest(action):
        return {"status": "conflict", "result": None}
    return {"status": "completed", "result": saved[1]}

if __name__ == "__main__":
    with demo.TemporaryDirectory() as folder:
        ledger = demo.Ledger(demo.Path(folder) / "exercise.db")
        try:
            action = {"kind": "close", "ticket_id": "T-7"}
            assert query_operation(ledger, "op-7", action)["status"] == "unknown"
            ledger.approve("a-7", action, 200)
            ledger.execute("op-7", "a-7", action, 100)
            result = query_operation(ledger, "op-7", action)
            assert result == {"status": "completed", "result": "closed:T-7"}
            assert query_operation(ledger, "op-7", {"kind": "close", "ticket_id": "T-8"})["status"] == "conflict"
            assert ledger.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0] == 1
            print(result)
        finally:
            ledger.close()
