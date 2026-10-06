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
    def test_bad_port_fails(self):
        for value in ["0", "65536", "abc"]:
            with self.assertRaises(ValueError):
                self.api["load_config"]({"PORT": value})

    def test_readiness_differs_from_liveness(self):
        value = self.api["health"](False)
        self.assertEqual(value["live"]["status"], 200)
        self.assertEqual(value["ready"]["status"], 503)

if __name__ == "__main__":
    unittest.main()
