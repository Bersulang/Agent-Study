"""新知识来源扩展参考：先建证据再回答，不伪造真实Embedding。"""
from pathlib import Path
import runpy

api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

class ExtendedAssistant(api["Assistant"]):
    def answer(self, tenant, query):
        # 使用已认证租户选择可见来源；该字典是明确标注的教学资料。
        documents = {"A": {"登录": {"source": "fixture-login-v1", "text": "教学流程：检查账号状态后联系支持"}}}
        for keyword, evidence in documents.get(tenant, {}).items():
            if keyword in query:
                return {"status": "answered", "evidence": evidence}
        return super().answer(tenant, query)

if __name__ == "__main__":
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as folder:
        assistant = ExtendedAssistant(Path(folder) / "extended.db")
        print("新增知识来源：", assistant.request("lab-a", "如何处理登录问题", "q1"))
        print("未知资料：", assistant.request("lab-a", "休假问题", "q2")["status"])
        print("跨租户无证据：", assistant.request("lab-b", "如何处理登录问题", "q3")["status"])
