"""并发等待期间交错推进；信号量限制同时运行数量。"""
import asyncio


async def query(ticket_id, limit):
    async with limit:
        await asyncio.sleep(0.01)
        return f"{ticket_id}: open"


async def main():
    limit = asyncio.Semaphore(2)
    tasks = []
    for number in range(3):
        # 调用async函数得到协程对象；gather会调度它们并收集结果。
        tasks.append(query(f"T-{number}", limit))
    return await asyncio.gather(*tasks)  # 星号将列表里的协程逐个传给gather。


if __name__ == "__main__":
    print(asyncio.run(main()))
