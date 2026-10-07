"""超时会请求取消任务；取消不会撤销已经发生的外部副作用。"""
import asyncio


async def slow_query():
    await asyncio.sleep(1)
    return "完成"


async def main():
    try:
        return await asyncio.wait_for(slow_query(), timeout=0.01)
    except TimeoutError:
        return "查询超时"


if __name__ == "__main__":
    print(asyncio.run(main()))
