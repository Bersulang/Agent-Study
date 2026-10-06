"""本地HTTP探针只验证Python客户端；它不是Java服务验收。"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from client import fetch_ticket

class Probe(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('X-Service-Token') != 'local-teaching-token':
            status, body = 401, {'error': 'invalid_service_token'}
        elif self.headers.get('X-User-Id') != 'alice' or self.headers.get('X-Tenant-Id') != 'acme':
            status, body = 403, {'error': 'tenant_mismatch'}
        else:
            status, body = 200, {'ticket': 'T-7', 'trace': self.headers.get('X-Trace-Id')}
        encoded = json.dumps(body).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *args):
        pass  # 断言负责验证，避免访问日志淹没测试输出。

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Probe)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_identity_and_trace_headers_arrive(self):
        self.assertEqual(fetch_ticket(self.url), {'status': 200, 'ticket': 'T-7', 'trace': 'trace-7'})

    def test_http_error_body_is_preserved(self):
        self.assertEqual(fetch_ticket(self.url, service_token='wrong'), {'status': 401, 'error': 'invalid_service_token'})

if __name__ == '__main__':
    unittest.main()
