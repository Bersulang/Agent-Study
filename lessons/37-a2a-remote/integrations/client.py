"""真实官方SDK客户端；--local在进程内访问ASGI，默认访问已启动的服务。"""
import asyncio
import sys
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, TextPart, TaskQueryParams

async def main(local=False):
    transport = None
    if local:
        from server import app
        transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, timeout=2) as http:
        resolver = A2ACardResolver(httpx_client=http, base_url='http://127.0.0.1:9999')
        card = await resolver.get_agent_card()
        print('发现技能:', [skill.id for skill in card.skills])
        # 选非流模式；ClientFactory依据Agent Card构造官方协议客户端。
        client = ClientFactory(ClientConfig(httpx_client=http, streaming=False)).create(card)
        message = Message(role='user', message_id=str(uuid4()), parts=[Part(root=TextPart(text='T-7'))])
        async for event in client.send_message(message):
            # Task结果事件是(task, update)二元组；消息型响应直接是Message。
            if isinstance(event, tuple):
                task = event[0]
                print('完成状态:', task.status.state.value)
                queried = await client.get_task(TaskQueryParams(id=task.id))
                print('查证产物:', queried.artifacts[0].parts[0].root.text)

if __name__ == '__main__':
    asyncio.run(main(local='--local' in sys.argv))
