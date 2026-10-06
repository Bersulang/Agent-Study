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
    def test_submission_requires_approval(self):
        with self.assertRaises(PermissionError):
            self.api["PageTask"]().submit(False)

    def test_repeat_submission_same_result(self):
        page = self.api["PageTask"]()
        self.assertEqual(page.submit(True), page.submit(True))
        self.assertEqual(page.state, "confirmed")

    def test_invalid_media_rejected(self):
        for mime,size in [("image/png", 0), ("audio/wav", 2_000_000), ("unknown", 10)]:
            with self.assertRaises(ValueError):
                self.api["check_media"](mime, size)

if __name__ == "__main__":
    unittest.main()
