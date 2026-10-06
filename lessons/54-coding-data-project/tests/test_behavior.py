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
    def test_outside_patch_rejected(self):
        with self.assertRaises(PermissionError):
            self.api["patch"](".", "../calc.py")

    def test_patch_must_match_old_content(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            (Path(folder) / "calc.py").write_text("unexpected", encoding="utf-8")
            with self.assertRaises(ValueError):
                self.api["patch"](folder, "calc.py")

    def test_report_denies_arbitrary_sql(self):
        with self.assertRaises(PermissionError):
            self.api["report"](None, "A", "DELETE FROM tickets")

    def test_real_test_turns_green(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            (Path(folder) / "calc.py").write_text(self.api["BEFORE"], encoding="utf-8")
            self.assertFalse(self.api["run_check"](folder)["passed"])
            self.api["patch"](folder, "calc.py")
            self.assertTrue(self.api["run_check"](folder)["passed"])

if __name__ == "__main__":
    unittest.main()
