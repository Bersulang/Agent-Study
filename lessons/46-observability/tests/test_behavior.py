"""课程行为回归测试：验证真实函数的成功与失败路径。"""
import runpy
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parents[1] / 'examples' / 'demo.py'

class BehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 加载教学实现，不执行其中的命令行演示入口。
        cls.api = runpy.run_path(str(CODE))
    def test_nested_secret_is_redacted(self):
        value = self.api["redact"]({"nested": [{"token": "secret"}]})
        self.assertEqual(value["nested"][0]["token"], "[REDACTED]")

    def test_error_span_is_recorded(self):
        events = []
        with self.assertRaises(TimeoutError):
            with self.api["span"](events, "r1", "tool"):
                raise TimeoutError("secret")
        self.assertEqual(events[0]["status"], "error")
        self.assertNotIn("secret", str(events))

    def test_negative_usage_is_invalid(self):
        with self.assertRaises(ValueError):
            self.api["estimate_cost"](-1, 1, 1, 1)

if __name__ == "__main__":
    unittest.main()
