"""配置与健康检查教具；默认不启动常驻HTTP服务。"""
from pathlib import Path

def load_config(environ):
    try:
        port = int(environ.get("PORT", "8080"))
    except ValueError as error:
        raise ValueError("PORT必须是整数") from error
    if not 1 <= port <= 65535:
        raise ValueError("PORT超出合法范围")
    data_dir = Path(environ.get("DATA_DIR", "artifacts/service-data"))
    return {"port": port, "data_dir": data_dir}

def health(dependency_ready):
    # 同一进程仍存活，但依赖故障时拒绝流量。
    return {"live": {"status": 200}, "ready": {"status": 200 if dependency_ready else 503}}

def startup_config(environ):
    """已有数据目录必须可实际写入；不在启动检查中隐式创建拼错的路径。"""
    import tempfile
    config = load_config(environ)
    directory = config["data_dir"]
    if not directory.exists():
        raise FileNotFoundError("数据目录不存在，请先显式创建")
    if not directory.is_dir():
        raise NotADirectoryError("DATA_DIR必须指向目录")
    # os.access在Windows不能可靠代表ACL实际结果；创建、写入、关闭真实临时文件。
    # TemporaryFile退出时删除探测文件，不保留业务内容，也不覆盖已有文件。
    try:
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b"startup-write-probe")
            probe.flush()
    except OSError as error:
        raise PermissionError("数据目录不可写") from error
    return config

if __name__ == "__main__":
    print("配置端口：", load_config({})["port"])
    print("正常健康：", health(True))
    print("依赖故障：", health(False))
    try:
        load_config({"PORT": "70000"})
    except ValueError as error:
        print("启动校验：", error)
