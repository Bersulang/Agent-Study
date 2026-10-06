"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def replay_events(service, task_id, session_id, after):
    if not isinstance(after, int) or after < 0:
        raise ValueError("invalid_cursor")
    task = service.tasks[task_id]
    if task["session"] != session_id:
        raise PermissionError("session_mismatch")
    return [{"seq": index + 1, "type": event} for index, event in enumerate(task["events"]) if index + 1 > after]

if __name__ == "__main__":
    service = demo.TaskService()
    key = service.create("session-7", "工单")
    service.advance(key)
    result = replay_events(service, key, "session-7", 1)
    assert result == [{"seq": 2, "type": "text"}, {"seq": 3, "type": "final"}]
    try:
        replay_events(service, key, "other", 0)
    except PermissionError:
        print("越会话访问已拒绝")
    else:
        raise AssertionError("必须隔离会话")
    print(result)
