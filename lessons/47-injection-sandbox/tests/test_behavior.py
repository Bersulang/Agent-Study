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
    def test_path_escape_blocked(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as root:
            with self.assertRaises(PermissionError):
                self.api["resolve_read"](root, "../secret.txt")

    def test_shell_capability_blocked(self):
        with self.assertRaises(PermissionError):
            self.api["execute_tool"](".", "shell", "x.txt")

    def test_credentials_url_blocked(self):
        self.assertFalse(self.api["allowed_origin"]("https://user@docs.example.com/x"))
        self.assertFalse(self.api["allowed_origin"]("https://docs.example.com:444/x"))

if __name__ == "__main__":
    unittest.main()
