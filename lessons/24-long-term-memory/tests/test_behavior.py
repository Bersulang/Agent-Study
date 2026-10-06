# 测试关注真实权限、预算、删除和恢复行为；不检查内部代码长相。
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo", Path(__file__).resolve().parents[1] / "examples/demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_boundary_and_failure(self):
        memory = demo.Memory()
        memory.put("u", "k", "v", "message:1", 10, True)
        self.assertIsNone(memory.get("other", "k", 1))
        self.assertIsNone(memory.get("u", "k", 10))
        with self.assertRaises(PermissionError):
            memory.put("u", "k", "new", "m", 20, False)
        self.assertEqual(memory.get("u", "k", 1), "v")
        memory.forget("u", "k")
        self.assertIsNone(memory.get("u", "k", 1))

if __name__ == "__main__":
    unittest.main()
