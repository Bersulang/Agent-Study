"""真实模型计划适配与离线契约测试，不默认调用付费API。"""
import json
import os
from pathlib import Path
import runpy

class ModelPlanner:
    def __init__(self, client):
        self.client = client

    def __call__(self, question):
        # 这是格式约束提示，安全仍由解析器与业务执行器负责。
        messages = [
            {"role": "system", "content": '只返回JSON。动作仅answer或draft。answer含query字符串；draft含title字符串。缺少标题返回空title，不推测。'},
            {"role": "user", "content": question},
        ]
        response = self.client.complete(messages)
        plan = json.loads(response["text"])
        if not isinstance(plan, dict):
            raise ValueError("计划必须是对象")
        action = plan.get("action")
        field = "query" if action == "answer" else "title" if action == "draft" else None
        if field is None or set(plan) != {"action", field} or not isinstance(plan[field], str):
            raise ValueError("模型计划不符合动作Schema")
        return plan

def real_planner():
    # 复用阶段08真实适配；网络操作只在显式调用计划时发生。
    root = Path(__file__).resolve().parents[3]
    adapter = runpy.run_path(str(root / "lessons/08-model-api/integrations/http_model.py"))["HTTPModel"]
    if not os.environ.get("MODEL_BASE_URL"):
        raise ValueError("请配置MODEL_BASE_URL、MODEL_API_KEY和MODEL_NAME")
    return ModelPlanner(adapter(os.environ["MODEL_BASE_URL"], os.environ.get("MODEL_API_KEY", ""), os.environ.get("MODEL_NAME", "")))

if __name__ == "__main__":
    class FixtureClient:
        def complete(self, messages):
            # 明确的固定数据夹具，仅验证适配契约，不伪称模型推理。
            return {"text": '{"action":"answer","query":"查询新资料"}'}
    print("离线模型计划契约：", ModelPlanner(FixtureClient())("查询新资料"))
