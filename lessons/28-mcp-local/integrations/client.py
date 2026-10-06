"""真实子进程MCP客户端：进入时连接，退出时关闭子进程，整次运行有超时。"""
import asyncio
from pathlib import Path
import sys

from mcp import Client, StdioServerParameters


async def main():
    server = Path(__file__).with_name("server.py")
    params = StdioServerParameters(command=sys.executable, args=[str(server)])
    # sys.executable使子进程使用同一个虚拟环境，而非PATH中的其他Python。
    async with asyncio.timeout(20):
        async with Client(params) as client:
            tools = await client.list_tools()
            names = [tool.name for tool in tools.tools]
            assert "get_ticket" in names
            print("tools", names)
            result = await client.call_tool("get_ticket", {"ticket_id": "T1"})
            assert not result.is_error
            assert result.structured_content is not None and result.structured_content["found"] is True
            print("result", result.structured_content)
            missing = await client.call_tool("missing", {})
            assert missing.is_error
            print("unknown_tool_is_error", missing.is_error)
            resource = await client.read_resource("policy://current")
            print("resource", resource.contents[0].text)
            prompt = await client.get_prompt("summarize_ticket", {"ticket_id": "T1"})
            print("prompt", prompt.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
