"""离线任务生命周期教具；真实 A2A SDK 服务位于 integrations。"""
class TaskRegistry:
    def __init__(self):
        self.tasks = {}

    def submit(self, task_id, text):
        if task_id in self.tasks:
            raise ValueError("task_already_exists")
        self.tasks[task_id] = {"status": "submitted", "text": text, "artifact": None}

    def finish(self, task_id):
        task = self.tasks[task_id]
        if task["status"] != "submitted":
            return  # 终态不能再次执行，例如取消后不能写产物。
        task["status"] = "working"
        task["artifact"] = "T-7: open"
        task["status"] = "completed"

    def cancel(self, task_id):
        task = self.tasks[task_id]
        if task["status"] in {"completed", "canceled"}:
            raise ValueError("task_not_cancelable")
        task["status"] = "canceled"

    def get(self, task_id):
        if task_id not in self.tasks:
            return {"error": "task_not_found"}
        task = self.tasks[task_id]
        return {"status": task["status"], "artifact": task["artifact"]}

def run_case(case):
    registry = TaskRegistry()
    if case == "unknown":
        return registry.get("missing")
    registry.submit("remote-7", "查询工单 T-7")
    if case == "cancel":
        registry.cancel("remote-7")
    registry.finish("remote-7")
    return registry.get("remote-7")

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'cancel', 'unknown']:
        print(case, run_case(case))
