"""检验课程验证器能发现缺课、断链，并忽略代码示例中的假链接。"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from tools.verify_course import discover_lessons, local_link_errors

class VerifierTests(unittest.TestCase):
    def test_missing_stages_fail(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "lessons/01-environment").mkdir(parents=True)
            # 只提供阶段01不能被报告为完整56阶段。
            with self.assertRaises(ValueError):
                discover_lessons(root)

    def test_duplicate_stage_fails(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for number in range(1, 57):
                (root / f"lessons/{number:02}-sample").mkdir(parents=True)
            (root / "lessons/01-duplicate").mkdir()
            with self.assertRaises(ValueError):
                discover_lessons(root)

    def test_broken_link_reported(self):
        with TemporaryDirectory() as folder:
            page = Path(folder) / "README.md"
            page.write_text("[missing](no-file.md)", encoding="utf-8")
            self.assertEqual(len(local_link_errors(page)), 1)

    def test_code_examples_and_external_urls_ignored(self):
        with TemporaryDirectory() as folder:
            page = Path(folder) / "README.md"
            page.write_text("```text\n[fake](example.md)\n```\n[web](https://example.com)\n", encoding="utf-8")
            self.assertEqual(local_link_errors(page), [])

if __name__ == "__main__":
    unittest.main()
