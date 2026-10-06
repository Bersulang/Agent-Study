"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

registry = {"versions": {}, "active": None}
bundle = {key: "v1" for key in api["REQUIRED"]}
metrics = {"success_rate": 1., "security_violations": []}
old = api["promote"](registry, bundle, metrics)
task = {"version": old}  # 启动时固化完整版本ID，之后不读取active别名。
for bad in [{"success_rate": .8, "security_violations": []}, {"success_rate": 1., "security_violations": ["leak"]}]:
    before = dict(registry["versions"])
    try:
        api["promote"](registry, {**bundle, "prompt": "bad"}, bad)
    except ValueError:
        assert registry["active"] == old and registry["versions"] == before
        print("坏版本拒绝；旧版保持活跃")
    else:
        raise AssertionError("坏版本不应发布")
new = api["promote"](registry, {**bundle, "prompt": "v2"}, metrics)
assert new != old and task["version"] == old
api["rollback"](registry, old)
assert registry["active"] == old
print("旧任务未漂移；安全回滚成功；CI示例见solutions/course-checks.yml")
