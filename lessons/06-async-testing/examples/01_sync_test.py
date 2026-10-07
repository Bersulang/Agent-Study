"""先用同步unittest表达业务预期，不需要第三方测试框架。"""
import unittest


def is_urgent(priority):
    return priority >= 4


class UrgencyTests(unittest.TestCase):
    def test_high_priority_is_urgent(self):
        self.assertTrue(is_urgent(4))


if __name__ == "__main__":
    unittest.main()
