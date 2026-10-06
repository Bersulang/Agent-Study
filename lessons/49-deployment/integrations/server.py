"""真实本地HTTP健康服务；生产服务使用适合的平台和应用服务器。"""
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from contextlib import closing
import runpy

CORE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

DATA = Path(os.environ.get("DATA_DIR", "artifacts/service-data"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 存活不依赖数据库；就绪执行真实查询而不只看进程。
        if self.path == "/health/live":
            status, body = 200, {"live": True}
        elif self.path == "/health/ready":
            try:
                with closing(sqlite3.connect(DATA / "service.db", timeout=1)) as connection:
                    connection.execute("SELECT 1").fetchone()
                status, body = 200, {"ready": True}
            except sqlite3.Error:
                status, body = 503, {"ready": False}
        else:
            status, body = 404, {"error": "not_found"}
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))

    def log_message(self, format, *args):
        # 不把请求路径和客户端信息无限制写日志；生产需结构化脱敏。
        return

if __name__ == "__main__":
    config = CORE["startup_config"](os.environ)
    DATA, port = config["data_dir"], config["port"]
    host = os.environ.get("HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Health service: http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
