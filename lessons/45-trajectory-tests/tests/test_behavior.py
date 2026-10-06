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
    def test_write_before_approval_is_blocked(self):
        with self.assertRaises(PermissionError):
            self.api["validate_trace"](["started", "write", "finished"])

    def test_double_write_is_rejected(self):
        with self.assertRaises(ValueError):
            self.api["validate_trace"](["started", "approved", "write", "write", "finished"])

    def test_revocation_is_effective(self):
        with self.assertRaises(PermissionError):
            self.api["validate_trace"](["started", "approved", "revoked", "write", "finished"])

    def test_read_only_trace_completes(self):
        self.assertEqual(self.api["validate_trace"](["started", "read", "finished"])["writes"], 0)

if __name__ == "__main__":
    unittest.main()
