"""检查器不能拒绝课程已有合格解法；只在临时副本中使用答案。

这是维护检查器的回归测试，不是学员验收命令，不写入任何学习进度。
"""
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from tools.check_exercise import execute_cases
from tools.exercise_checks import build_cases

ROOT = Path(__file__).resolve().parents[1]


class ReferenceCompatibilityTests(unittest.TestCase):
    def test_existing_function_exercises_accept_reference_behavior(self):
        # 后期项目的solve适配器也只检查代码子集，不代表完整项目验收。
        for stage in range(1, 57):
            with self.subTest(stage=stage), TemporaryDirectory() as temporary:
                original = next((ROOT / "lessons").glob(f"{stage:02d}-*"))
                lesson = Path(temporary) / original.name
                shutil.copytree(original, lesson, ignore=shutil.ignore_patterns("__pycache__"))
                filename = "startup_card.py" if stage == 1 else "practice.py"
                answer = "startup_card.py" if stage == 1 else "solution.py"
                shutil.copyfile(lesson / "solutions" / answer, lesson / "exercises" / filename)
                if stage == 13:
                    shutil.copyfile(lesson / "solutions/feedback_solution.py",
                                    lesson / "exercises/feedback_practice.py")
                result = execute_cases(build_cases(stage, lesson))
                failed = [(row["name"], row["detail"]) for row in result["cases"] if not row["passed"]]
                self.assertTrue(result["passed"], failed)


if __name__ == "__main__":
    unittest.main()
