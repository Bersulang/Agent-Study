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
    def test_missing_prediction_is_rejected(self):
        with self.assertRaises(ValueError):
            self.api["evaluate"](self.api["CASES"], [])

    def test_security_failure_blocks_release(self):
        rows = [dict(id=c["id"], action=c["expected"]) for c in self.api["CASES"]]
        rows[-1]["action"] = "answer"
        report = self.api["evaluate"](self.api["CASES"], rows)
        self.assertFalse(report["release_allowed"])
        self.assertEqual(report["security_violations"], ["unsafe-1"])

    def test_duplicate_prediction_rejected(self):
        rows = [dict(id=c["id"], action=c["expected"]) for c in self.api["CASES"]]
        with self.assertRaises(ValueError):
            self.api["evaluate"](self.api["CASES"], rows + [rows[0]])

if __name__ == "__main__":
    unittest.main()
