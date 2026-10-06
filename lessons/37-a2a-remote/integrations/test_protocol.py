"""官方SDK应用协议测试，覆盖发现、产物、查证与input-required取消。"""
import unittest
from starlette.testclient import TestClient
from server import app

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def rpc(self, method, params):
        return self.client.post('/', json={'jsonrpc': '2.0', 'id': 'r7', 'method': method, 'params': params})

    def test_card_exposes_ticket_skill(self):
        response = self.client.get('/.well-known/agent-card.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['skills'][0]['id'], 'ticket-status')

    def test_task_result_can_be_queried(self):
        response = self.rpc('message/send', {'message': {'kind': 'message', 'role': 'user', 'messageId': 'message-7', 'parts': [{'kind': 'text', 'text': 'T-7'}]}})
        self.assertEqual(response.status_code, 200)
        task = response.json()['result']
        self.assertEqual(task['status']['state'], 'completed')
        self.assertEqual(task['artifacts'][0]['parts'][0]['text'], 'T-7: open')
        queried = self.rpc('tasks/get', {'id': task['id']}).json()['result']
        self.assertEqual(queried['id'], task['id'])

    def test_input_required_task_can_be_canceled(self):
        response = self.rpc('message/send', {'message': {'kind': 'message', 'role': 'user', 'messageId': 'message-8', 'parts': [{'kind': 'text', 'text': 'wait'}]}})
        self.assertEqual(response.status_code, 200)
        task = response.json()['result']
        self.assertEqual(task['status']['state'], 'input-required')
        canceled = self.rpc('tasks/cancel', {'id': task['id']}).json()['result']
        self.assertEqual(canceled['status']['state'], 'canceled')
        self.assertFalse(canceled.get('artifacts'))

if __name__ == '__main__':
    unittest.main()
