"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
import asyncio

async def solve(data):
    semaphore = asyncio.Semaphore(2)
    async def one(identity, delay):
        async def operation():
            async with semaphore:
                await asyncio.sleep(delay)
                return {"id": identity, "ok": True}
        try:
            return await asyncio.wait_for(operation(), 0.02)
        except TimeoutError:
            return {"id": identity, "error": "timeout"}
    return await asyncio.gather(*(one(identity, delay) for identity, delay in data))

if __name__ == "__main__":
    print(asyncio.run(solve([("T1", 0.001), ("T2", 0.1)])))
