"""离线服务领域层。实际 FastAPI 路由、事件流及页面见 integrations。"""
class TaskService:
    def __init__(self):
        self.tasks = {}

    def create(self, session_id, prompt):
        if not isinstance(session_id, str) or not session_id.strip() or not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("invalid_request")
        task_id = f"task-{len(self.tasks) + 1}"
        self.tasks[task_id] = {"session": session_id, "status": "running", "events": ["progress"]}
        return task_id

    def advance(self, task_id):
        task = self.tasks[task_id]
        if task["status"] == "running":
            task["events"].extend(["text", "final"])
            task["status"] = "completed"

    def cancel(self, task_id):
        task = self.tasks[task_id]
        if task["status"] != "running":
            raise ValueError("task_not_cancelable")
        task["status"] = "canceled"
        task["events"].append("canceled")

    def read(self, task_id):
        task = self.tasks[task_id]
        return {"status": task["status"], "events": list(task["events"])}

def run_case(case):
    service = TaskService()
    try:
        key = service.create("session-7", "" if case == "invalid" else "查询工单")
    except ValueError as exc:
        return {"error": str(exc), "tasks": len(service.tasks)}
    if case == "cancel":
        service.cancel(key)
    service.advance(key)
    return service.read(key)

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'cancel', 'invalid']:
        print(case, run_case(case))
