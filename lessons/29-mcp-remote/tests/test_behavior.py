# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        calls = []
        def denied():
            calls.append(1)
            raise PermissionError("401")
        with self.assertRaises(PermissionError):
            demo.call_read(denied)
        self.assertEqual(len(calls), 1)
        with self.assertRaises(demo.RemoteError):
            demo.compatible(["deleted"], ["get_ticket"])
        with self.assertRaises(demo.RemoteError):
            demo.call_read(lambda: (_ for _ in ()).throw(ConnectionError()))

if __name__ == "__main__":
    unittest.main()
