"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def list_recoverable(store):
    rows = store.db.execute("SELECT id,state,version FROM tasks WHERE state IN (?, ?) ORDER BY id", ("new", "ready")).fetchall()
    return [{"id": row[0], "state": row[1], "version": row[2]} for row in rows]

if __name__ == "__main__":
    with demo.TemporaryDirectory() as folder:
        path = demo.Path(folder) / "exercise.db"
        store = demo.Store(path)
        try:
            store.create("T-7")
            store.create("T-8")
            store.save("T-8", "completed", 0)
        finally:
            store.close()
        recovered = demo.Store(path)
        try:
            result = list_recoverable(recovered)
            assert result == [{"id": "T-7", "state": "new", "version": 0}]
            print(result)
        finally:
            recovered.close()
