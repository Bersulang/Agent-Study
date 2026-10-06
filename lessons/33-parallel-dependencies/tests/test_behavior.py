"""回归：删除边界保护会改变任务结果或副作用数量。"""
import importlib.util
from pathlib import Path
import unittest

# 根据测试文件定位示例，不依赖 PowerShell 的当前搜索路径。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_success(self):
        # 断言业务结果；失败分支还检查状态或副作用未越界。
        self.assertEqual(demo.run_case('success'), {'status': 'completed', 'knowledge': 'policy-v2', 'ticket': 'T-7', 'summary': 'policy-v2 / T-7', 'peak': 2})

    def test_timeout(self):
        # 断言业务结果；失败分支还检查状态或副作用未越界。
        self.assertEqual(demo.run_case('timeout'), {'status': 'partial', 'knowledge': 'policy-v2', 'ticket': 'timeout', 'summary': None, 'peak': 2})

if __name__ == "__main__":
    unittest.main()
