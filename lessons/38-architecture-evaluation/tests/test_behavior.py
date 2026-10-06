"""回归：删除边界保护会改变任务结果或副作用数量。"""
import importlib.util
from pathlib import Path
import unittest

# 根据测试文件定位示例，不依赖 PowerShell 的当前搜索路径。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class BehaviorTests(unittest.TestCase):
    def test_comparison(self):
        # 断言业务结果；失败分支还检查状态或副作用未越界。
        self.assertEqual(demo.run_case('comparison'), {'single_correct': 2, 'workflow_correct': 3, 'multi_correct': 3, 'selected': 'workflow'})

    def test_regression(self):
        # 断言业务结果；失败分支还检查状态或副作用未越界。
        self.assertEqual(demo.run_case('regression'), {'single_correct': 2, 'workflow_correct': 2, 'multi_correct': 3, 'selected': 'multi'})

if __name__ == "__main__":
    unittest.main()
