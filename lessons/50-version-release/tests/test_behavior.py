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
    def test_bad_release_does_not_change_active(self):
        registry = {"versions": {}, "active": None}
        bundle = {key: "v1" for key in self.api["REQUIRED"]}
        old = self.api["promote"](registry, bundle, {"success_rate": 1.0, "security_violations": []})
        with self.assertRaises(ValueError):
            self.api["promote"](registry, {**bundle, "prompt": "v2"}, {"success_rate": 0.1, "security_violations": []})
        self.assertEqual(registry["active"], old)

    def test_missing_version_field_fails(self):
        with self.assertRaises(ValueError):
            self.api["fingerprint"]({"code": "v1"})

    def test_unknown_rollback_fails(self):
        with self.assertRaises(ValueError):
            self.api["rollback"]({"versions": {}, "active": None}, "unknown")

if __name__ == "__main__":
    unittest.main()
