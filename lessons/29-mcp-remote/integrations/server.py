"""真实Streamable HTTP服务；仅监听回环地址，不提供生产认证。"""
import argparse

from mcp.server import MCPServer
from pydantic import BaseModel

mcp = MCPServer("RemoteTicketStudy", version="1.0.0")


class TicketResult(BaseModel):
    # 声明输出模型，供SDK提供可靠的structured_content而非仅文本块。
    found: bool
    ticket_id: str
    status: str | None


@mcp.tool()
def get_ticket(ticket_id: str) -> TicketResult:
    """只读工单查询教学数据；真实项目应基于可信身份验证对象访问权限。"""
    return TicketResult(found=ticket_id == "T1", ticket_id=ticket_id, status="open" if ticket_id == "T1" else None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    mcp.run(transport="streamable-http", host="127.0.0.1", port=args.port)
