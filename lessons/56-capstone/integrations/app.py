"""毕业参考的实际FastAPI接口；认证Token仅为本地教学夹具。"""
from pathlib import Path
import runpy
import time
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

CORE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

class TaskInput(BaseModel):
    # 对输入显式约束，复杂Schema仍需在工具层和业务层再次验证。
    question: str = Field(min_length=1, max_length=1000)
    key: str = Field(min_length=1, max_length=64)

class ApprovalInput(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    digest: str = Field(min_length=64, max_length=64)

def create_app(database):
    assistant = CORE["Assistant"](database)
    app = FastAPI(title="企业助手教学API")

    def token_from(header):
        if not header or not header.startswith("Bearer "):
            raise HTTPException(401, "缺少教学身份Token")
        return header[7:]

    def invoke(function, *args, **kwargs):
        try:
            return function(*args, **kwargs)
        except PermissionError:
            # 对客户端不泄漏租户、数据库或凭证细节。
            raise HTTPException(403, "身份、权限或审批条件不满足")
        except ValueError:
            raise HTTPException(422, "参数或幂等条件不满足")

    @app.post("/tasks")
    def task(body: TaskInput, authorization: str | None = Header(default=None)):
        token = token_from(authorization)
        return invoke(assistant.request, token, body.question, body.key, now=time.time())

    @app.post("/approvals")
    def approval(body: ApprovalInput, authorization: str | None = Header(default=None)):
        token = token_from(authorization)
        return invoke(assistant.approve, token, body.key, body.digest, now=time.time())

    @app.get("/health")
    def health():
        return {"status": "ok", "model_mode": "offline_fixture"}

    return app

def factory():
    # Uvicorn --factory调用时才创建数据目录，不在导入测试模块时写业务数据。
    directory = Path(__file__).resolve().parents[3] / "artifacts/capstone"
    directory.mkdir(parents=True, exist_ok=True)
    return create_app(directory / "assistant.db")
