"""实际HTTP MCP客户端：发现并调用，使用有限超时，默认只连接本机。"""
import argparse
import asyncio

from mcp import Client


async def query(url):
    async with asyncio.timeout(15):
        async with Client(url) as client:
            tools = await client.list_tools()
            names = [tool.name for tool in tools.tools]
            if "get_ticket" not in names:
                raise ValueError("服务能力已变化：没有get_ticket")
            result = await client.call_tool("get_ticket", {"ticket_id": "T1"})
            if result.is_error:
                raise RuntimeError("工具执行失败")
            print("tools", names)
            print("result", result.structured_content)
            return result.structured_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8765/mcp")
    args = parser.parse_args()
    asyncio.run(query(args.url))
