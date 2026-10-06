"""用响应丢失模拟“已写入但调用者不知道”，验证重复调用不重复写。"""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("reliability_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
class ReliabilityTests(unittest.TestCase):
    def test_retry_keeps_one_effect(self):
        store = demo.Store()
        result = demo.retry_create(store, "request-1", "title", attempts=2)
        self.assertEqual(result["id"], "T1")
        self.assertEqual(len(store.tickets), 1)
    def test_same_key_different_payload_rejected(self):
        store = demo.Store()
        demo.retry_create(store, "k", "a")
        with self.assertRaises(ValueError):
            demo.retry_create(store, "k", "b")
    def test_no_permission_no_effect(self):
        store = demo.Store()
        with self.assertRaises(PermissionError):
            demo.retry_create(store, "k", "a", allowed=False)
        self.assertEqual(store.tickets, [])
    def test_zero_attempts_rejected(self):
        with self.assertRaises(ValueError):
            demo.retry_create(demo.Store(), "k", "a", attempts=0)
if __name__ == "__main__":
    unittest.main()
