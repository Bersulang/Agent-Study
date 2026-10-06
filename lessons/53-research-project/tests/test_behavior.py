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
    def test_conflict_requires_review(self):
        result = self.api["research"](["policy-a", "policy-b"])
        self.assertEqual(result["status"], "needs_review")

    def test_stale_source_is_not_evidence(self):
        self.assertEqual(self.api["research"](["old-policy"])["status"], "no_evidence")

    def test_duplicate_source_not_double_counted(self):
        result = self.api["research"](["policy-a", "policy-a"])
        self.assertEqual(len(result["claims"]["reply_hours"]), 1)

    def test_budget_exhaustion(self):
        with self.assertRaises(ValueError):
            self.api["research"](["policy-a", "policy-b"], budget=1)

if __name__ == "__main__":
    unittest.main()
