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
    def test_missing_backup_fails(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                self.api["restore"](Path(folder) / "missing.db", Path(folder) / "target.db")

    def test_corrupt_backup_fails(self):
        import sqlite3
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            broken = Path(folder) / "broken.db"
            broken.write_bytes(b"not a database")
            with self.assertRaises(sqlite3.DatabaseError):
                self.api["restore"](broken, Path(folder) / "target.db")

    def test_feedback_is_deduplicated(self):
        rows = self.api["candidates"]([{"category": "failure", "case_id": "c1"}] * 2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "pending_review")

    def test_snapshot_releases_file_handles(self):
        import sqlite3
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            source, target = Path(folder) / "source.db", Path(folder) / "target.db"
            con = sqlite3.connect(source)
            con.execute("CREATE TABLE records(id INTEGER)")
            con.commit()
            con.close()
            self.api["snapshot"](source, target)
            # Windows中未释放连接时，这两个删除操作会报文件占用。
            source.unlink()
            target.unlink()

    def test_missing_source_does_not_create_backup(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            missing, target = Path(folder) / "missing.db", Path(folder) / "backup.db"
            with self.assertRaises(FileNotFoundError):
                self.api["snapshot"](missing, target)
            self.assertFalse(missing.exists())
            self.assertFalse(target.exists())

    def test_restore_does_not_overwrite_existing_database(self):
        import sqlite3
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            backup, target = Path(folder) / "empty.db", Path(folder) / "existing.db"
            sqlite3.connect(backup).close()
            con = sqlite3.connect(target)
            con.execute("CREATE TABLE preserved(id INTEGER)")
            con.commit()
            con.close()
            with self.assertRaises(ValueError):
                self.api["restore"](backup, target)

    def test_restore_rejects_missing_business_schema(self):
        import sqlite3
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            backup, target = Path(folder) / "empty.db", Path(folder) / "new.db"
            sqlite3.connect(backup).close()
            with self.assertRaises(ValueError):
                self.api["restore"](backup, target)
            self.assertFalse(target.exists())

if __name__ == "__main__":
    unittest.main()
