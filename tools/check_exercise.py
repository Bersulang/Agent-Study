"""校验学员练习并记录结果；不以课程演示或参考答案代替学员作业。

项目根目录运行：python tools/check_exercise.py 01
查看当前结果：python tools/check_exercise.py --status
仅验证、不更新学习记录：python tools/check_exercise.py 01 --no-record
"""
import argparse
import asyncio
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
STATUS_TEXT = {"passed": "代码校验通过", "failed": "待修改", "stale": "代码或规则已变化，待重验"}
START = "<!-- exercise-checks:start -->"
END = "<!-- exercise-checks:end -->"


def lesson_path(root, stage):
    """以课程目录为准定位阶段，拒绝越界编号和目录逃逸。"""
    root = Path(root).resolve()
    catalog = json.loads((root / "course.json").read_text(encoding="utf-8"))
    for lesson in catalog["lessons"]:
        if lesson["stage"] == stage:
            path = (root / lesson["path"]).resolve()
            if not path.is_relative_to(root / "lessons") or not path.is_dir():
                raise ValueError("课程目录无效")
            return path
    raise ValueError("阶段编号必须在01—56之间")


def fingerprint(root, stage):
    """作业、可复用示例和检查规则一起签名；改过的代码需要重新验收。"""
    root = Path(root).resolve()
    lesson = lesson_path(root, stage)
    files = list((lesson / "exercises").rglob("*.py"))
    files += list((lesson / "examples").rglob("*.py"))
    files += list((root / "tools/exercise_checks").rglob("*.py"))
    files += [root / "tools/check_exercise.py", root / "course.json"]
    digest = hashlib.sha256()
    for path in sorted(set(files)):
        if path.is_file():
            digest.update(str(path.relative_to(root)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def failed_result(name, detail):
    return {"passed": False, "cases": [{"name": name, "passed": False, "detail": detail}]}


def execute_cases(cases):
    """每个检查独立报告。退出进程、未实现或零检查都不能当成通过。"""
    results = []
    for name, check in cases:
        output = io.StringIO()
        row = {"name": name, "passed": False, "detail": ""}
        with redirect_stdout(output), redirect_stderr(output):
            try:
                outcome = check()
                if inspect.isawaitable(outcome):
                    # 异步检查必须真正运行，创建协程本身并不代表检查通过。
                    asyncio.run(outcome)
                row["passed"] = True
            except BaseException:
                row["detail"] = traceback.format_exc(limit=5)[-4000:]
        row["output"] = output.getvalue()[-4000:]
        results.append(row)
    if not results:
        return failed_result("检查规则", "没有可执行的检查项，不能标记通过")
    return {"passed": all(row["passed"] for row in results), "cases": results}


def worker(root, stage):
    """隔离子进程执行课程检查；导入失败也产生结构化错误报告。"""
    sys.path.insert(0, str(root))
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            from tools.exercise_checks import build_cases
            lesson = lesson_path(root, stage)
            # 和直接运行practice.py一样，允许练习把代码拆到同目录模块。
            sys.path.insert(0, str(lesson / "exercises"))
            result = execute_cases(build_cases(stage, lesson))
        except BaseException:
            result = failed_result("加载练习与检查规则", traceback.format_exc(limit=6)[-4000:])
    result["load_output"] = output.getvalue()[-4000:]
    print(json.dumps(result, ensure_ascii=False))


def run_checks(root, stage, timeout=20):
    """子进程保证死循环有上限；这不是限制文件或网络权限的沙箱。"""
    root = Path(root).resolve()
    before = fingerprint(root, stage)
    command = [sys.executable, str(Path(__file__).resolve()), str(stage),
               "--_worker", "--_root", str(root)]
    # 强制UTF-8并移除优化标志，防止python -O跳过行为断言。
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    environment.pop("PYTHONOPTIMIZE", None)
    try:
        process = subprocess.run(command, cwd=root, env=environment, capture_output=True,
                                 text=True, encoding="utf-8", timeout=timeout)
        if process.returncode != 0:
            result = failed_result("练习进程", process.stderr[-4000:] or "练习进程异常退出")
        else:
            result = json.loads(process.stdout)
            if not isinstance(result.get("cases"), list) or not result["cases"]:
                result = failed_result("检查报告", "报告缺少有效检查项")
            else:
                result["passed"] = all(row.get("passed") is True for row in result["cases"])
    except subprocess.TimeoutExpired:
        result = failed_result("运行时间", f"校验超时（超过{timeout}秒），可能存在死循环或阻塞；已停止检查进程")
    except (ValueError, TypeError, AttributeError):
        result = failed_result("检查报告", "检查进程未返回有效报告，请检查顶层退出或输出")
    if fingerprint(root, stage) != before:
        result["cases"].append({"name": "代码版本", "passed": False,
                                "detail": "检查期间代码发生变化，请保存后重新运行"})
        result["passed"] = False
    result.update(stage=stage, fingerprint=before,
                  checked_at=datetime.now(timezone.utc).isoformat(), command=command)
    return result


def atomic_write(path, text):
    """同目录临时文件替换，避免中断留下半份JSON或Markdown。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_state(root):
    path = Path(root) / ".local/exercise-progress.json"
    if not path.exists():
        return {"schema_version": 1, "stages": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("schema_version") != 1 or not isinstance(state.get("stages"), dict):
        raise ValueError("学习记录格式无效，原文件保留，请先修复记录")
    return state


def render_progress(root, state):
    """只更新练习状态和专属自动区块，保留能力结论、当前阶段和老师反馈。"""
    path = Path(root) / "docs/progress.md"
    page = path.read_text(encoding="utf-8")
    for number, record in state["stages"].items():
        # 既有五列进度表：阶段、课程、材料、练习、能力。只改练习列。
        pattern = rf"^(\| {number} \|[^\n]*?\|[^\n]*?\|)[^|\n]*(\|[^\n]*\|)$"
        label = STATUS_TEXT[record["status"]]
        page = re.sub(pattern, lambda match: match[1] + " " + label + " " + match[2], page, flags=re.MULTILINE)
    current = re.search(r"当前学习阶段：\*\*(\d+)", page)
    if current and f"{int(current[1]):02}" in state["stages"]:
        label = STATUS_TEXT[state["stages"][f"{int(current[1]):02}"]["status"]]
        page = re.sub(r"^- 练习状态：[^\n]*", "- 练习状态：" + label + "。", page, flags=re.MULTILINE)
    lines = [START, "## 练习自动校验记录", "",
             "本区由校验命令生成，仅代表当前练习的代码检查。概念解释、项目交付与真实集成能力分别验收。",
             "修改代码后重新运行校验；查看状态时也会检查代码和规则是否变化。", "",
             "| 阶段 | 代码状态 | 通过检查数 | 检查时间（UTC） |", "| --- | --- | --- | --- |"]
    for number, record in sorted(state["stages"].items()):
        cases = record.get("cases", [])
        passed = sum(row.get("passed") is True for row in cases)
        lines.append(f"| {number} | {STATUS_TEXT[record['status']]} | {passed}/{len(cases)} | {record.get('checked_at', '未记录')} |")
    if not state["stages"]:
        lines.append("| — | 尚未运行学员练习校验 | — | — |")
    lines.append(END)
    section = "\n".join(lines)
    if START in page and END in page:
        page = page[:page.index(START)] + section + page[page.index(END) + len(END):]
    else:
        page = page.rstrip() + "\n\n" + section + "\n"
    atomic_write(path, page)


def record_result(root, result):
    """记录最后一次结果；失败覆盖旧通过，但不自动推进整课学习阶段。"""
    root = Path(root)
    state = read_state(root)
    number = f"{result['stage']:02}"
    record = {**result, "status": "passed" if result["passed"] else "failed"}
    if not record.get("checked_at"):
        record["checked_at"] = datetime.now(timezone.utc).isoformat()
    state["stages"][number] = record
    atomic_write(root / f"artifacts/exercise-checks/{number}-latest.json",
                 json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    # JSON是唯一事实记录；Markdown是展示，可用--status从JSON重新生成。
    atomic_write(root / ".local/exercise-progress.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    render_progress(root, state)
    return state


def refresh_status(root):
    """通过记录仅对原代码版本有效，改动后标为待重验。"""
    state = read_state(root)
    for number, record in state["stages"].items():
        if record.get("fingerprint") != fingerprint(root, int(number)):
            record["status"] = "stale"
    atomic_write(Path(root) / ".local/exercise-progress.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    render_progress(root, state)
    return state


def main():
    parser = argparse.ArgumentParser(description="检查你的练习代码，自动记录结果，无需手填运行输出。")
    parser.add_argument("stage", nargs="?", type=int, help="阶段编号，例如01")
    parser.add_argument("--status", action="store_true", help="查看记录，并把修改过的代码标为待重验")
    parser.add_argument("--no-record", action="store_true", help="只检查，不修改学习进度（材料维护使用）")
    parser.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--_root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = args._root.resolve()
    if args._worker:
        worker(root, args.stage)
        return 0
    try:
        if args.status:
            if args.stage is not None or args.no_record:
                parser.error("--status不能与阶段编号或--no-record同时使用")
            state = refresh_status(root)
            if not state["stages"]:
                print("尚无练习校验记录。从01开始：python tools/check_exercise.py 01")
            for number, record in sorted(state["stages"].items()):
                print(f"阶段{number}：{STATUS_TEXT[record['status']]}")
            return 0
        if args.stage is None:
            parser.error("请提供阶段编号，例如01；或用--status查看记录")
        result = run_checks(root, args.stage)
        for row in result["cases"]:
            print(f"[{'通过' if row['passed'] else '未通过'}] {row['name']}")
            if not row["passed"]:
                # 终端先给结论，完整回溯自动写入报告，不让初学者淹没在内部栈里。
                lines = row["detail"].strip().splitlines()
                print("  " + (lines[-1] if lines else "结果不符合要求"))
        print("代码校验通过；完整课程能力仍需对应验收。" if result["passed"] else "练习尚未通过，请按提示修改后重试。")
        if not args.no_record:
            record_result(root, result)
            print("结果已自动保存到docs/progress.md及.local/exercise-progress.json。")
        return 0 if result["passed"] else 1
    except (OSError, ValueError) as error:
        print(f"无法完成校验或保存记录：{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
