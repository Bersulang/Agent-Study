"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

from tempfile import TemporaryDirectory
with TemporaryDirectory() as folder:
    config = api["startup_config"]({"DATA_DIR": folder, "PORT": "9000"})
    assert config["port"] == 9000 and list(Path(folder).iterdir()) == []
    file = Path(folder) / "file.txt"
    file.write_text("fixture", encoding="utf-8")
    for directory, error_type in [(Path(folder) / "missing", FileNotFoundError), (file, NotADirectoryError)]:
        try:
            api["startup_config"]({"DATA_DIR": str(directory)})
        except error_type:
            print("启动拒绝非法数据目录")
        else:
            raise AssertionError("非法目录不应启动")
assert api["health"](False) == {"live": {"status": 200}, "ready": {"status": 503}}
try:
    api["load_config"]({"PORT": "70000"})
except ValueError:
    print("启动拒绝非法端口")
print("依赖失效：存活200，就绪503；实际写权限失败由回归测试覆盖")
print("Docker重启与卷持久验证：见solutions/README.md，本次未运行Docker")

def solve(data):
    """检查启动目录与存活/就绪探针的离线规则。"""
    if not data["data_dir_writable"]:
        raise ValueError("数据目录不可写")
    return {"liveness_status": 200,
            "readiness_status": 200 if data["dependency_healthy"] else 503}
