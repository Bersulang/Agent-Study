"""官方MCP SDK stdio服务：stdout专用于协议，日志请使用stderr。"""
from mcp.server import MCPServer
from pydantic import BaseModel

mcp = MCPServer("TicketStudy", version="1.0.0")
TICKETS = {"T1": {"status": "open", "title": "登录失败"}}


class TicketResult(BaseModel):
    # 明确输出字段让SDK生成结构化输出契约；裸dict注解不会自动保证structured_content。
    found: bool
    ticket: dict | None


@mcp.tool()
def get_ticket(ticket_id: str) -> TicketResult:
    """按工单标识查询本地教学数据；不修改业务记录。"""
    if not ticket_id:
        raise ValueError("ticket_id不能为空")
    row = TICKETS.get(ticket_id)
    return TicketResult(found=row is not None, ticket=dict(row) if row else None)


@mcp.resource("policy://current")
def policy() -> str:
    """返回当前教学政策资料。"""
    return "付款前必须审批。"


@mcp.prompt()
def summarize_ticket(ticket_id: str) -> str:
    """生成用户可选择的工单摘要提示模板。"""
    return f"请先查询工单{ticket_id}，再基于真实字段总结状态。"


if __name__ == "__main__":
    mcp.run(transport="stdio")
