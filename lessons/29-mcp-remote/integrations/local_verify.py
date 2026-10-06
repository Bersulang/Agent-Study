"""有限运行验证：启动本机HTTP服务、调用、停止并确认断连，finally清理子进程。"""
import asyncio
from pathlib import Path
import socket
import subprocess
import sys
import time

from client import query


def main():
    # 选择可用临时端口；绑定释放与服务启动之间仍有竞争，冲突时明确失败。
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    process = subprocess.Popen([sys.executable, str(Path(__file__).with_name("server.py")), "--port", str(port)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}/mcp"
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("HTTP服务启动失败，请单独运行server.py查看日志")
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", port)) == 0:
                    break
            time.sleep(0.1)
        else:
            raise TimeoutError("HTTP服务未在15秒内启动")
        result = asyncio.run(query(url))
        assert result["found"] is True
        print("真实HTTP MCP读取通过")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    try:
        asyncio.run(query(url))
    except Exception:
        print("服务停止后连接按预期失败；本例不盲目重试写操作")
    else:
        raise AssertionError("服务已停止却仍能连接")


if __name__ == "__main__":
    main()
