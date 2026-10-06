"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def renew(queue, job_id, owner, token, now, ttl):
    if ttl <= 0:
        raise ValueError("ttl必须大于0")
    updated = queue.db.execute("UPDATE jobs SET expires=? WHERE id=? AND owner=? AND token=? AND state='leased' AND expires>?",
                               (now + ttl, job_id, owner, token, now))
    return updated.rowcount == 1

if __name__ == "__main__":
    with demo.TemporaryDirectory() as folder:
        queue = demo.Queue(demo.Path(folder) / "exercise.db")
        try:
            queue.enqueue("T-7")
            first = queue.claim("T-7", "worker-a", 100)
            assert renew(queue, "T-7", "worker-a", first, 105, 10)
            assert not renew(queue, "T-7", "worker-a", first, 115, 10)
            second = queue.claim("T-7", "worker-b", 116)
            assert not renew(queue, "T-7", "worker-a", first, 117, 10)
            assert renew(queue, "T-7", "worker-b", second, 117, 10)
            print("续租成功；边界过期和旧token续租已拒绝")
        finally:
            queue.close()
