"""本地模拟I/O；无网络，不宣称真实接口性能。"""
import asyncio

async def query(identity, delay, semaphore):
    # async with获取许可，异常与取消时也会释放。
    async with semaphore:
        await asyncio.sleep(delay)
        return {"id": identity, "status": "open"}

async def safe_query(identity, delay, semaphore, timeout=0.1):
    try:
        return await asyncio.wait_for(query(identity, delay, semaphore), timeout)
    except TimeoutError:
        return {"id": identity, "error": "timeout"}

async def collect():
    semaphore = asyncio.Semaphore(2)
    # gather结果按输入次序排列，不按完成先后；模拟一条超时。
    return await asyncio.gather(
        safe_query("T1", 0.001, semaphore),
        safe_query("T2", 0.002, semaphore),
        safe_query("T3", 0.2, semaphore),
    )

if __name__ == "__main__":
    print(asyncio.run(collect()))
