"""自动验收必须检查学员代码；超时、空测试和过期结果不得算通过。"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from tools.check_exercise import execute_cases, fingerprint, record_result, run_checks, refresh_status


class ExerciseRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.lesson = self.root / "lessons/01-environment"
        (self.lesson / "exercises").mkdir(parents=True)
        (self.lesson / "exercises/startup_card.py").write_text('print("待填写")', encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "tools/exercise_checks").mkdir(parents=True)
        (self.root / "course.json").write_text(json.dumps({"lessons": [
            {"stage": 1, "path": "lessons/01-environment", "ability_status": "pending"}
        ]}), encoding="utf-8")
        (self.root / "docs/progress.md").write_text(
            "# 进度\n\n保留老师反馈。\n| 01 | 课程 | 已准备 | 未提交 | 待验收 |\n", encoding="utf-8")

    def result(self, passed=True):
        return {"stage": 1, "passed": passed, "fingerprint": fingerprint(self.root, 1),
                "cases": [{"name": "四行输出", "passed": passed, "detail": ""}]}

    def test_empty_suite_is_not_success(self):
        self.assertFalse(execute_cases([])["passed"])

    def test_async_case_is_awaited_and_failure_is_not_lost(self):
        async def failed():
            raise AssertionError("异步结果不符合要求")
        self.assertFalse(execute_cases([("异步检查", failed)])["passed"])

    def test_failed_case_and_system_exit_are_recorded(self):
        def failed():
            raise AssertionError("必须输出四行")
        def exits():
            raise SystemExit(0)
        result = execute_cases([("错误结果", failed), ("提前退出", exits)])
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["cases"]), 2)
        self.assertIn("必须输出四行", result["cases"][0]["detail"])

    def test_pass_marks_exercise_without_marking_full_ability(self):
        record_result(self.root, self.result())
        page = (self.root / "docs/progress.md").read_text(encoding="utf-8")
        self.assertIn("代码校验通过", page)
        self.assertIn("待验收", page)
        self.assertIn("保留老师反馈", page)
        self.assertIn("| 01 | 课程 | 已准备 | 代码校验通过 | 待验收 |", page)
        self.assertEqual(json.loads((self.root / "course.json").read_text())["lessons"][0]["ability_status"], "pending")

    def test_new_failure_replaces_previous_pass(self):
        record_result(self.root, self.result())
        record_result(self.root, self.result(False))
        self.assertNotIn("代码校验通过", (self.root / "docs/progress.md").read_text(encoding="utf-8"))

    def test_changed_exercise_invalidates_a_past_pass(self):
        record_result(self.root, self.result())
        (self.lesson / "exercises/startup_card.py").write_text('print("changed")', encoding="utf-8")
        state = refresh_status(self.root)
        self.assertEqual(state["stages"]["01"]["status"], "stale")
        self.assertIn("待重验", (self.root / "docs/progress.md").read_text(encoding="utf-8"))

    def test_case_changes_also_invalidate_pass(self):
        record_result(self.root, self.result())
        (self.root / "tools/exercise_checks/new.py").write_text("# 新的边界测试", encoding="utf-8")
        self.assertEqual(refresh_status(self.root)["stages"]["01"]["status"], "stale")

    def test_child_timeout_is_failure(self):
        # 临时课程中的检查器只为验证runner超时，不会执行正式课程或网络请求。
        (self.root / "tools/exercise_checks/__init__.py").write_text(
            "import time\ndef build_cases(stage, lesson):\n    return [('挂起', lambda: time.sleep(10))]\n",
            encoding="utf-8")
        result = run_checks(self.root, 1, timeout=0.4)
        self.assertFalse(result["passed"])
        self.assertIn("超时", result["cases"][0]["detail"])

    def test_modified_during_run_is_not_marked_pass(self):
        (self.root / "tools/exercise_checks/__init__.py").write_text(
            "def build_cases(stage, lesson):\n"
            "    def modify():\n"
            "        (lesson / 'exercises/startup_card.py').write_text('changed', encoding='utf-8')\n"
            "    return [('修改输入文件', modify)]\n", encoding="utf-8")
        self.assertFalse(run_checks(self.root, 1)["passed"])

    def test_cli_records_only_without_no_record(self):
        # 检验保存流程使用临时课程，不能把维护者样例记为真实学员进度。
        (self.root / "tools/exercise_checks/__init__.py").write_text(
            "def build_cases(stage, lesson):\n    return [('可运行', lambda: None)]\n", encoding="utf-8")
        script = Path(__file__).resolve().parents[1] / "tools/check_exercise.py"
        command = [sys.executable, str(script), "01", "--_root", str(self.root)]
        result = subprocess.run(command + ["--no-record"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / ".local/exercise-progress.json").exists())
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((self.root / ".local/exercise-progress.json").read_text(encoding="utf-8"))
        self.assertEqual(record["stages"]["01"]["status"], "passed")

    def test_optimization_environment_does_not_disable_checks(self):
        (self.root / "tools/exercise_checks/__init__.py").write_text(
            "def build_cases(stage, lesson):\n"
            "    def fail():\n        assert False, 'must fail'\n"
            "    return [('断言有效', fail)]\n", encoding="utf-8")
        from unittest.mock import patch
        with patch.dict(os.environ, {"PYTHONOPTIMIZE": "1"}):
            self.assertFalse(run_checks(self.root, 1)["passed"])


if __name__ == "__main__":
    unittest.main()
