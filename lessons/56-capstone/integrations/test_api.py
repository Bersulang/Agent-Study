"""实际FastAPI接口测试，覆盖审批、幂等与跨租户失败。"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from fastapi.testclient import TestClient
from app import create_app

class ApiTests(unittest.TestCase):
    def setUp(self):
        # 每个测试使用独立临时数据库，不影响真实课程成果。
        self.temp = TemporaryDirectory()
        self.client = TestClient(create_app(Path(self.temp.name) / "test.db"))
        self.headers = {"Authorization": "Bearer lab-a"}

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def test_approval_replay_and_tenant_boundary(self):
        draft = self.client.post("/tasks", headers=self.headers,
                                 json={"question": "创建工单:问题", "key": "k1"})
        self.assertEqual(draft.status_code, 200)
        body = {"key": "k1", "digest": draft.json()["digest"]}
        created = self.client.post("/approvals", headers=self.headers, json=body)
        repeated = self.client.post("/approvals", headers=self.headers, json=body)
        self.assertEqual(created.json(), repeated.json())
        denied = self.client.post("/approvals", headers={"Authorization": "Bearer lab-b"}, json=body)
        self.assertEqual(denied.status_code, 403)

    def test_missing_identity_and_invalid_input(self):
        self.assertEqual(self.client.post("/tasks", json={"question": "政策", "key": "q1"}).status_code, 401)
        self.assertEqual(self.client.post("/tasks", headers=self.headers, json={"question": "", "key": "q1"}).status_code, 422)

if __name__ == "__main__":
    unittest.main()
