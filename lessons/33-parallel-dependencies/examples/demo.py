"""独立查询并行，汇总依赖两个查询成功；超时后不生成假结论。"""
import asyncio

async def execute(slow_ticket=False):
    semaphore = asyncio.Semaphore(2)
    active = 0
    peak = 0

    async def query(value, delay):
        nonlocal active, peak  # 修改外层变量；不是创建局部同名变量。
        async with semaphore:
            active += 1
            peak = max(peak, active)
            try:
                await asyncio.sleep(delay)  # 代表可取消的异步 I/O。
                return value
            finally:
                active -= 1  # 取消也必须释放活动计数。

    async def bounded(value, delay):
        try:
            return await asyncio.wait_for(query(value, delay), timeout=0.1)
        except TimeoutError:
            return "timeout"

    knowledge, ticket = await asyncio.gather(
        bounded("policy-v2", 0.01), bounded("T-7", 0.5 if slow_ticket else 0.02))
    complete = "timeout" not in (knowledge, ticket)
    return {"status": "completed" if complete else "partial", "knowledge": knowledge,
            "ticket": ticket, "summary": f"{knowledge} / {ticket}" if complete else None, "peak": peak}

def run_case(case):
    return asyncio.run(execute(slow_ticket=case == "timeout"))

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'timeout']:
        print(case, run_case(case))
