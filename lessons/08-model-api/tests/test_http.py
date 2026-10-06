"""不调用付费模型；Mock HTTP验证序列化、认证头与错误契约。"""
import importlib.util
import io
import json
from email.message import Message
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import HTTPHandler, HTTPSHandler
from urllib.response import addinfourl

path = Path(__file__).resolve().parents[1] / "integrations" / "http_model.py"
spec = importlib.util.spec_from_file_location("http_model", path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)

class Response(io.BytesIO):
    """模拟urllib上下文响应，测试时不需要外网。"""

class HTTPTests(unittest.TestCase):
    def test_payload_and_result(self):
        body = {"choices": [{"message": {"content": "answer"}}], "usage": {"prompt_tokens": 3, "completion_tokens": 2}}
        with patch.object(model, "open_request", return_value=Response(json.dumps(body).encode())) as send:
            adapter = model.HTTPModel("https://api.example.test/v1", "fake", "test-model")
            result = adapter.complete([{"role": "user", "content": "hi"}])
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.example.test/v1/chat/completions")
        self.assertEqual(json.loads(request.data)["model"], "test-model")
        self.assertEqual(result["usage"], {"input_tokens": 3, "output_tokens": 2})
        self.assertEqual(result["text"], "answer")

    def test_http_error_does_not_leak_body(self):
        failure = HTTPError("https://api.example.test", 401, "unauthorized", {}, io.BytesIO(b'secret-body'))
        with patch.object(model, "open_request", side_effect=failure):
            with self.assertRaisesRegex(model.ModelAPIError, "HTTP 401") as caught:
                model.HTTPModel("https://api.example.test/v1", "fake", "test").complete([])
        self.assertNotIn("secret-body", str(caught.exception))

    def test_refusal_is_explicit(self):
        body = {"choices": [{"message": {"content": None, "refusal": "拒绝"}}]}
        with patch.object(model, "open_request", return_value=Response(json.dumps(body).encode())):
            with self.assertRaisesRegex(model.ModelAPIError, "拒答"):
                model.HTTPModel("https://api.example.test/v1", "fake", "test").complete([])

    def test_key_missing(self):
        with self.assertRaises(ValueError):
            model.HTTPModel("https://api.example.test/v1", "", "test")

    def test_plain_http_rejected(self):
        with self.assertRaises(ValueError):
            model.HTTPModel("http://remote.example/v1", "fake", "test")

    def assert_redirect_blocked(self, status, target):
        requests = []
        def simulated_transport(handler, request):
            # 替换最终HTTP/HTTPS传输，不替换urllib的重定向处理。
            # 所有地址均为example.test，认证头只有假Token，绝不建立连接。
            requests.append(request)
            headers = Message()
            if len(requests) == 1:
                headers["Location"] = target
                response = addinfourl(io.BytesIO(b"redirect-body"), headers, request.full_url, status)
                response.msg = "Redirect"
            else:
                body = {"choices": [{"message": {"content": "unexpected redirected answer"}}]}
                response = addinfourl(io.BytesIO(json.dumps(body).encode()), headers, request.full_url, 200)
                response.msg = "OK"
            return response
        with patch.object(HTTPSHandler, "https_open", simulated_transport), patch.object(HTTPHandler, "http_open", simulated_transport):
            with self.assertRaisesRegex(model.ModelAPIError, "重定向") as caught:
                model.HTTPModel("https://api.example.test/v1", "fake-token", "test").complete([])
        self.assertEqual(len(requests), 1, "不能产生携带认证头的第二次请求")
        self.assertNotIn("fake-token", str(caught.exception))
        self.assertNotIn("redirect-body", str(caught.exception))
        self.assertNotIn(target, str(caught.exception))

    def test_cross_origin_redirect_is_blocked(self):
        self.assert_redirect_blocked(302, "https://other.example.test/stolen")

    def test_https_downgrade_redirect_is_blocked(self):
        self.assert_redirect_blocked(302, "http://api.example.test/stolen")

    def test_every_3xx_is_blocked_including_307_308(self):
        for status in range(300, 400):
            with self.subTest(status=status):
                self.assert_redirect_blocked(status, "https://api.example.test/changed")

if __name__ == "__main__":
    unittest.main()
