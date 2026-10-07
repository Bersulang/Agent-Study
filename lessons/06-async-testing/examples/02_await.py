"""await让出事件循环；asyncio.run负责驱动顶层协程。"""
import asyncio


async def query_ticket():
    await asyncio.sleep(0.01)  # 用短暂停顿模拟等待网络，不访问真实服务。
    return "T-1: open"


if __name__ == "__main__":
    print(asyncio.run(query_ticket()))
