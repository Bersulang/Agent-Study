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
    def test_cross_tenant_access_rejected(self):
        with self.assertRaises(PermissionError):
            self.api["read_ticket"]("session-a", "B", "T-001", {}, [])

    def test_cache_is_scoped(self):
        cache, audit = {}, []
        a = self.api["read_ticket"]("session-a", "A", "T-001", cache, audit)
        b = self.api["read_ticket"]("session-b", "B", "T-001", cache, audit)
        self.assertNotEqual(a, b)
        self.assertEqual(len(cache), 2)

    def test_denial_is_audited(self):
        audit = []
        with self.assertRaises(PermissionError):
            self.api["read_ticket"]("session-a", "B", "T-001", {}, audit)
        self.assertFalse(audit[0]["allowed"])
        self.assertNotIn("session-a", str(audit))

if __name__ == "__main__":
    unittest.main()
