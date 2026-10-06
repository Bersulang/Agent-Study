"""扩展需求回归：真实状态、失败边界和副作用保持。"""
import runpy
import unittest
from pathlib import Path

class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))
    def test_startup_rejects_missing_or_file_directory(self):
        from tempfile import TemporaryDirectory
        self.assertIn("startup_config", self.api, "扩展功能尚未实现")
        with TemporaryDirectory() as folder:
            root = Path(folder)
            file = root / "file.txt"
            file.write_text("fixture", encoding="utf-8")
            for directory in [root / "missing", file]:
                with self.assertRaises((FileNotFoundError, NotADirectoryError)):
                    self.api["startup_config"]({"DATA_DIR": str(directory)})

    def test_startup_rejects_failed_write_probe(self):
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        self.assertIn("startup_config", self.api, "扩展功能尚未实现")
        with TemporaryDirectory() as folder:
            # Windows下只读属性不等于ACL；在创建文件边界模拟OS拒写。
            with patch("tempfile.TemporaryFile", side_effect=PermissionError("denied")):
                with self.assertRaises(PermissionError):
                    self.api["startup_config"]({"DATA_DIR": folder})

    def test_startup_write_probe_is_cleaned(self):
        from tempfile import TemporaryDirectory
        self.assertIn("startup_config", self.api, "扩展功能尚未实现")
        with TemporaryDirectory() as folder:
            self.api["startup_config"]({"DATA_DIR": folder})
            self.assertEqual(list(Path(folder).iterdir()), [])

if __name__ == "__main__":
    unittest.main()
