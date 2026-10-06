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
    def test_exhaustion_and_refill(self):
        bucket = self.api["TokenBucket"](1, 1)
        self.assertTrue(bucket.allow(0))
        self.assertFalse(bucket.allow(0))
        self.assertTrue(bucket.allow(1))

    def test_invalid_cost_rejected(self):
        bucket = self.api["TokenBucket"](1, 1)
        with self.assertRaises(ValueError):
            bucket.allow(0, -1)

    def test_tail_latency_visible(self):
        self.assertEqual(self.api["percentile"]([10] * 18 + [200, 400], 0.95), 200)

if __name__ == "__main__":
    unittest.main()
