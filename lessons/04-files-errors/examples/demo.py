"""临时目录读写，不在项目中留下测试数据。"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

def load_tickets(path):
    # with保证读取成功或失败后文件句柄均关闭。
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("工单文件必须是列表")
    for ticket in data:
        if not isinstance(ticket, dict) or not isinstance(ticket.get("id"), str):
            raise ValueError("每个工单必须包含字符串id")
    return data

def main():
    # 临时目录退出后自动清理，适合可重复演示。
    with TemporaryDirectory() as temporary:
        path = Path(temporary) / "tickets.json"
        path.write_text(json.dumps([{"id": "T1", "title": "无法登录"}], ensure_ascii=False), encoding="utf-8")
        print(f"读取：{load_tickets(path)}")
        path.write_text("{broken", encoding="utf-8")
        try:
            load_tickets(path)
        except json.JSONDecodeError:
            # 保留“损坏”的错误语义，不伪造成没有工单。
            print("读取失败：JSON损坏，保留错误并等待修复")

if __name__ == "__main__":
    main()
