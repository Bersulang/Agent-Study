"""行为检查本身必须识别未完成作业并接受符合契约的独立实现。"""
from pathlib import Path
import asyncio
import inspect
import shutil
import tempfile
import unittest

from tools.exercise_checks import build_cases
from tools.exercise_checks.foundation import _call_solve


ROOT = Path(__file__).resolve().parents[1]


class ExerciseCheckTests(unittest.TestCase):
    def test_stage_one_still_rejects_objectively_incomplete_cards(self):
        from tools.check_exercise import execute_cases
        # 每个反例只破坏一项客观要求，防止放宽措辞后丢失基本检查。
        valid = '# 名称\nprint("小站")\n# 用途\nprint("整理任务")\n# 能力\nprint("显示文字")\n# 目标\nprint("读取输入")\n'
        invalid = [valid.replace('print("小站")', 'print("待填写：我的助手名称")'),
                   valid.replace('print("整理任务")', 'print("")'),
                   valid.replace('print("整理任务")', 'print("小站")'),
                   valid.replace('# 用途\n', ''),
                   valid + 'print("多余一行")\n',
                   valid.replace('print("小站")', 'print("小站"')]
        for source in invalid:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as folder:
                lesson = Path(folder)
                (lesson / 'exercises').mkdir()
                (lesson / 'exercises/startup_card.py').write_text(source, encoding='utf-8')
                self.assertFalse(execute_cases(build_cases(1, lesson))['passed'])

    def test_stage_one_accepts_free_wording_without_required_labels(self):
        # 不复制学员文件；用独立样例保护自然表达与包含todo的合法名称。
        cards = [
            ['企业工单助手', '用于学习agent开发', '未做任何接入', '接入模型api'],
            ['Todo小站', '整理我的待办', '只能展示这张卡片', '支持输入任务'],
        ]
        for lines in cards:
            with self.subTest(lines=lines), tempfile.TemporaryDirectory() as folder:
                lesson = Path(folder)
                (lesson / 'exercises').mkdir()
                source = ''.join(f'# {label}\nprint({line!r})\n' for label, line in
                                 zip(['名称', '用途', '当前能力', '下一步目标'], lines))
                (lesson / 'exercises/startup_card.py').write_text(source, encoding='utf-8')
                for _, check in build_cases(1, lesson):
                    check()

    def test_every_stage_has_multiple_named_behavior_checks(self):
        for stage in range(1, 57):
            with self.subTest(stage=stage):
                cases = build_cases(stage, ROOT / "lessons" / _lesson_folder(stage))
                self.assertGreaterEqual(len(cases), 3)
                self.assertTrue(all(name and callable(check) for name, check in cases))

    def test_original_unfinished_skeletons_do_not_pass(self):
        for stage in range(1, 57):
            with self.subTest(stage=stage):
                folder = next((ROOT / "lessons").glob(f"{stage:02d}-*"))
                # 用临时副本重置学生练习，永远不要求用户的真实作业保持未完成。
                with tempfile.TemporaryDirectory() as temporary:
                    lesson = Path(temporary) / folder.name
                    shutil.copytree(folder, lesson)
                    exercises = lesson / "exercises"
                    if stage == 1:
                        (exercises / "startup_card.py").write_text(
                            'print("待填写")\n', encoding="utf-8")
                    cases = build_cases(stage, lesson)
                    failures = []
                    for name, check in cases:
                        try:
                            result = check()
                            if inspect.isawaitable(result):
                                asyncio.run(result)
                        except Exception as error:
                            failures.append((name, error))
                    self.assertTrue(failures, "未完成的练习骨架被错误标为通过")
                    self.assertTrue(all("缺少练习文件" not in str(error) for _, error in failures),
                                    f"检查必须运行到练习文件，不能只因缺文件失败：{failures}")

    def test_stage_one_accepts_a_valid_student_startup_card(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            (exercises / "startup_card.py").write_text(
                '# 显示助手名称。\nprint("客服助手")\n'
                '# 说明程序用途。\nprint("当前用途：查看工单")\n'
                '# 说明目前能力。\nprint("当前能力：尚未连接外部服务")\n'
                '# 说明下一步目标。\nprint("下一步目标：处理工单状态")\n',
                encoding="utf-8",
            )
            for _, check in build_cases(1, lesson):
                check()

    def test_stage_one_rejects_placeholders_and_missing_chinese_comments(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            (exercises / "startup_card.py").write_text(
                'print("待填写：我的助手名称")\nprint("用途")\n'
                'print("能力")\nprint("下一步")\n', encoding="utf-8"
            )
            failures = 0
            for _, check in build_cases(1, lesson):
                try:
                    check()
                except AssertionError:
                    failures += 1
            self.assertGreaterEqual(failures, 1)

    def test_stage_two_passes_semantic_outputs_and_rejects_wrong_behavior(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            student_file = exercises / "practice.py"
            student_file.write_text(
                'def solve(data):\n'
                '    rows = [row for row in data if row["status"] == "open"]\n'
                '    counts = {}\n'
                '    for row in rows: counts[row["department"]] = counts.get(row["department"], 0) + 1\n'
                '    return {"open_ids": [row["id"] for row in rows], "by_department": counts}\n',
                encoding="utf-8",
            )
            for _, check in build_cases(2, lesson):
                check()

            student_file.write_text(
                'def solve(data):\n    return {"open_ids": [], "by_department": {}}\n',
                encoding="utf-8",
            )
            failures = 0
            for _, check in build_cases(2, lesson):
                try:
                    check()
                except AssertionError:
                    failures += 1
            self.assertGreaterEqual(failures, 1)

    def test_stage_seventeen_accepts_semantic_dedupe_and_rejects_source_loss(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            student_file = exercises / "practice.py"
            student_file.write_text(
                'def solve(items):\n'
                '    chunks, errors = {}, []\n'
                '    for source, text in items:\n'
                '        if not text.strip(): errors.append({"source": source})\n'
                '        else: chunks.setdefault(text, []).append(source)\n'
                '    return {"chunks": [{"text": text, "locations": sources} for text, sources in chunks.items()], "errors": errors}\n',
                encoding="utf-8",
            )
            for _, check in build_cases(17, lesson):
                check()
            student_file.write_text(
                'def solve(items):\n'
                '    return {"chunks": [{"text": text, "locations": [source]} for source, text in items if text], "errors": []}\n',
                encoding="utf-8",
            )
            failures = []
            for name, check in build_cases(17, lesson):
                try:
                    check()
                except AssertionError:
                    failures.append(name)
            self.assertIn("重复正文保留所有来源", failures)
            self.assertIn("错误资料不阻断同批其他资料", failures)

    def test_reloading_same_path_and_length_uses_current_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            student_file = exercises / "practice.py"
            student_file.write_text('def solve(data): return 1\n', encoding="utf-8")
            self.assertEqual(_call_solve(lesson, []), 1)
            student_file.write_text('def solve(data): return 2\n', encoding="utf-8")
            self.assertEqual(_call_solve(lesson, []), 2)

    def test_stage_thirty_accepts_and_rejects_role_routing_behavior(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            (exercises / "practice.py").write_text(
                'def batch_route(requests, allowed_roles):\n'
                '    routes = [{"role": "human" if not text.strip() or text not in {"政策", "工单"} else ("knowledge" if text == "政策" else "ticket")} for text in requests]\n'
                '    for route in routes:\n        if route["role"] not in allowed_roles: route["role"] = "human"\n'
                '    counts = {name: sum(row["role"] == name for row in routes) for name in {"knowledge", "ticket", "human"}}\n'
                '    return {"routes": routes, "counts": counts}\n',
                encoding="utf-8",
            )
            for _, check in build_cases(30, lesson):
                check()
            (exercises / "practice.py").write_text(
                'def batch_route(requests, allowed_roles):\n'
                '    return {"routes": [{"role": "ticket"} for _ in requests], "counts": {"ticket": len(requests)}}\n',
                encoding="utf-8",
            )
            failures = []
            for name, check in build_cases(30, lesson):
                try:
                    check()
                except AssertionError:
                    failures.append(name)
            self.assertIn("未授权职责路由转人工", failures)

    def test_stage_forty_four_checks_evaluation_behavior_not_file_presence(self):
        with tempfile.TemporaryDirectory() as temporary:
            lesson = Path(temporary)
            exercises = lesson / "exercises"
            exercises.mkdir()
            (exercises / "practice.py").write_text(
                'def solve(data):\n'
                '    cases, predictions = data["cases"], data["predictions"]\n'
                '    ids = [row["id"] for row in predictions]\n'
                '    if len(ids) != len(set(ids)) or set(ids) != {row["id"] for row in cases}: raise ValueError("预测集不匹配")\n'
                '    scores = [int(next(row["action"] == case["expected"] for row in predictions if row["id"] == case["id"])) for case in cases]\n'
                '    by_category = {category: sum(score for score, case in zip(scores, cases) if case["category"] == category) / sum(case["category"] == category for case in cases) for category in {case["category"] for case in cases}}\n'
                '    return {"success_rate": sum(scores) / len(scores), "by_category": by_category, "release": sum(scores) / len(scores) >= data["threshold"] and not any(row.get("security_violation") for row in predictions)}\n',
                encoding="utf-8",
            )
            for _, check in build_cases(44, lesson):
                check()


def _lesson_folder(stage):
    return next(folder.name for folder in (ROOT / "lessons").iterdir()
                if folder.is_dir() and folder.name.startswith(f"{stage:02d}-"))


if __name__ == "__main__":
    unittest.main()
