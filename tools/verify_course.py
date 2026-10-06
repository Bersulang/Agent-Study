"""统一检查课程完整性、源码、链接、默认案例和回归测试。

从项目根目录执行：python tools/verify_course.py。
不安装依赖，不调用真实模型，不启动远程服务；报告写入artifacts。
"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def discover_lessons(root):
    """阶段必须01—56连续且唯一，避免空目录或重复编号被忽略。"""
    folders = sorted(path for path in (Path(root) / "lessons").iterdir()
                     if path.is_dir() and re.match(r"^\d{2}-", path.name))
    numbers = [int(path.name[:2]) for path in folders]
    if numbers != list(range(1, 57)):
        raise ValueError(f"阶段缺失或重复：{numbers}")
    return folders

def local_link_errors(path):
    """检查Markdown本地文件链接，忽略围栏中的教学示例和外部URL。"""
    path = Path(path)
    source = path.read_text(encoding="utf-8")
    if source.count("```") % 2:
        return [f"{path}: 代码围栏未闭合"]
    # 代码示例可能展示不存在的示意路径，它们不是导航链接。
    source = re.sub(r"```.*?```", "", source, flags=re.DOTALL)
    errors = []
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source):
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        local = target.split("#", 1)[0].strip("<>")
        if local and not (path.parent / local).exists():
            errors.append(f"{path}: {target}")
    return errors

def run_command(arguments, root, timeout=60):
    """参数列表启动子进程，有限等待；失败保留输出而不伪报通过。"""
    environ = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    try:
        result = subprocess.run(arguments, cwd=root, env=environ,
                                capture_output=True, text=True, encoding="utf-8", timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"command": arguments, "passed": False, "error": "timeout"}
    return {"command": arguments, "passed": result.returncode == 0,
            "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}

def verify(root, run=True):
    root = Path(root).resolve()
    folders = discover_lessons(root)
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version.split()[0], "stages": len(folders),
              "structural_errors": [], "commands": [], "source_count": 0,
              "markdown_count": 0, "unit_tests": 0}
    for folder in folders:
        required = ["README.md"]
        if folder.name[:2] != "01":
            required += ["knowledge.md", "examples/demo.py", "exercises/README.md",
                         "exercises/practice.py", "solutions/solution.py"]
        for name in required:
            if not (folder / name).is_file():
                report["structural_errors"].append(f"缺少材料：{folder.name}/{name}")
        for name in ["README.md", "knowledge.md"]:
            page = folder / name
            if page.exists() and len(page.read_text(encoding="utf-8")) < 400:
                report["structural_errors"].append(f"材料过短，需人工审查：{folder.name}/{name}")

    # 只遍历课程源码与项目文档，避免把虚拟环境依赖当作自己的课程。
    paths = [*root.glob("*.md")]
    for directory in ["docs", "lessons", "tools", "tests"]:
        paths.extend((root / directory).rglob("*.md"))
        for source in (root / directory).rglob("*.py"):
            report["source_count"] += 1
            try:
                compile(source.read_text(encoding="utf-8"), str(source), "exec")
            except (SyntaxError, UnicodeError) as error:
                report["structural_errors"].append(f"源码错误：{source}: {error}")
    for page in paths:
        report["markdown_count"] += 1
        report["structural_errors"].extend(local_link_errors(page))

    if run:
        for folder in folders:
            if folder.name.startswith("01-"):
                scripts = [*sorted((folder / "examples").glob("*.py")),
                           folder / "exercises/startup_card.py", folder / "solutions/startup_card.py"]
            else:
                scripts = [folder / "examples/demo.py", folder / "exercises/practice.py",
                           folder / "solutions/solution.py"]
            for script in scripts:
                if script.is_file():
                    report["commands"].append(run_command([sys.executable, str(script)], root))
            # 每课独立子进程，避免同名demo模块和测试全局状态互相污染。
            if (folder / "tests").is_dir():
                result = run_command([sys.executable, "-m", "unittest", "discover", "-s", str(folder / "tests"), "-v"], root)
                report["commands"].append(result)
                count = re.search(r"Ran (\d+) tests?", result.get("stderr", ""))
                if count:
                    report["unit_tests"] += int(count.group(1))
            print(f"Checked stage {folder.name[:2]}", flush=True)
        root_tests = run_command([sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-v"], root)
        report["commands"].append(root_tests)
        count = re.search(r"Ran (\d+) tests?", root_tests.get("stderr", ""))
        if count:
            report["unit_tests"] += int(count.group(1))
    report["passed"] = not report["structural_errors"] and all(row["passed"] for row in report["commands"])
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-only", action="store_true", help="仅检查结构、语法和本地链接")
    arguments = parser.parse_args()
    report = verify(ROOT, run=not arguments.static_only)
    output = ROOT / "artifacts/verification-report.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [row for row in report["commands"] if not row["passed"]]
    print(f"stages={report['stages']} python_files={report['source_count']} markdown={report['markdown_count']} commands={len(report['commands'])} tests={report['unit_tests']}")
    for error in report["structural_errors"]:
        print(error)
    for row in failed:
        print(row["command"], row.get("stderr", row.get("error", "failed")))
    print("PASS" if report["passed"] else "FAIL", f"report={output}")
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
