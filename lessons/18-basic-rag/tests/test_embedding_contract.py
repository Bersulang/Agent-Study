"""只验证HTTP适配契约和数学边界，固定数值夹具不代表真实embedding质量。"""
import importlib.util
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import unittest

spec = importlib.util.spec_from_file_location("provider", Path(__file__).resolve().parents[1] / "integrations/ollama_embeddings.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)


class ContractTests(unittest.TestCase):
    def test_cosine_rejects_invalid_dimensions_and_zero(self):
        self.assertAlmostEqual(provider.cosine([1, 0], [1, 0]), 1.0)
        with self.assertRaises(ValueError):
            provider.cosine([1], [1, 2])
        with self.assertRaises(ValueError):
            provider.cosine([0, 0], [1, 1])

    def test_http_request_and_response_mapping(self):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                requests.append((self.path, body))
                # 已知向量仅是协议夹具，不声称由模型产生。
                payload = json.dumps({"embeddings": [[1.0, 0.0], [0.0, 1.0]]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass  # 测试不打印HTTP访问日志，断言仍检查实际请求。

        server = HTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            adapter = provider.OllamaEmbeddings("fixture-model", f"http://127.0.0.1:{server.server_port}")
            self.assertEqual(adapter.embed(["one", "two"]), [[1.0, 0.0], [0.0, 1.0]])
            self.assertEqual(requests[0][0], "/api/embed")
            self.assertEqual(requests[0][1]["input"], ["one", "two"])
            self.assertFalse(requests[0][1]["truncate"])
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
