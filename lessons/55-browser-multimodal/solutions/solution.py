"""参考答案：先完成练习，再比较扩展行为与错误处理。"""
import runpy
from pathlib import Path

# 复用本阶段函数，不跨阶段隐式共享状态；不会调用演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'examples/demo.py'))

page = api["PageTask"]()
try:
    page.submit(False)
except PermissionError:
    print("未审批提交被拒绝")
first = page.submit(True)
assert page.state == "confirmed"
assert page.submit(True) == first
print("后置条件与去重：", first)
for mime, size in [("image/png", 0), ("application/executable", 10), ("audio/wav", 2_000_000)]:
    try:
        api["check_media"](mime, size)
    except ValueError:
        print("拒绝输入：", mime, size)
