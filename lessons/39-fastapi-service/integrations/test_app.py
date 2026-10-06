"""真实ASGI接口回归；不启动常驻端口，不需要模型凭据。"""
import unittest
import shutil
import subprocess
from fastapi.testclient import TestClient
from app import app, service

class APITests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), '可选Node环境未安装，只跳过页面脚本语法检查')
    def test_page_javascript_parses(self):
        # 检查真实响应中的脚本，而非Python源文件中的转义形式。
        html = self.client.get('/').text
        script = html.split('<script>')[1].split('</script>')[0]
        parsed = subprocess.run(['node', '--check'], input=script, text=True, capture_output=True)
        self.assertEqual(parsed.returncode, 0, parsed.stderr)

    def setUp(self):
        # 每个案例清理领域状态，防止测试顺序影响结果。
        service.tasks.clear()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_invalid_prompt_creates_no_task(self):
        response = self.client.post('/tasks', json={'session_id': 's7', 'prompt': ''})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(len(service.tasks), 0)

    def test_complete_replay_and_session_isolation(self):
        response = self.client.post('/tasks', json={'session_id': 's7', 'prompt': '工单'})
        self.assertEqual(response.status_code, 201)
        key = response.json()['task_id']
        headers = {'X-Session-Id': 's7'}
        self.assertEqual(self.client.post(f'/tasks/{key}/advance', headers=headers).status_code, 200)
        stream = self.client.get(f'/tasks/{key}/events?after=1', headers=headers)
        self.assertEqual(stream.status_code, 200)
        self.assertIn('event: text', stream.text)
        self.assertIn('event: final', stream.text)
        self.assertNotIn('event: progress', stream.text)
        self.assertEqual(self.client.get(f'/tasks/{key}', headers={'X-Session-Id': 'other'}).status_code, 404)

    def test_cancel_prevents_final_and_rejects_repeat_cancel(self):
        response = self.client.post('/tasks', json={'session_id': 's7', 'prompt': '工单'})
        self.assertEqual(response.status_code, 201)
        key = response.json()['task_id']
        headers = {'X-Session-Id': 's7'}
        self.assertEqual(self.client.delete(f'/tasks/{key}', headers=headers).status_code, 200)
        self.client.post(f'/tasks/{key}/advance', headers=headers)
        task = self.client.get(f'/tasks/{key}', headers=headers).json()
        self.assertEqual(task['status'], 'canceled')
        self.assertNotIn('final', task['events'])
        self.assertEqual(self.client.delete(f'/tasks/{key}', headers=headers).status_code, 409)

if __name__ == '__main__':
    unittest.main()
