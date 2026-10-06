"""异步契约测试：隔离事件循环，用可控协程代替网络。"""
import asyncio
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("async_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class QueryTests(unittest.IsolatedAsyncioTestCase):
    async def test_success(self):
        self.assertEqual(await demo.safe_query("T1", 0, asyncio.Semaphore(1)), {"id": "T1", "status": "open"})

    async def test_timeout(self):
        result = await demo.safe_query("T2", 1, asyncio.Semaphore(1), timeout=0.001)
        self.assertEqual(result, {"id": "T2", "error": "timeout"})

    async def test_cancel_propagates(self):
        # 外部取消属于生命周期事件，不能变成业务成功。
        task = asyncio.create_task(demo.safe_query("T3", 1, asyncio.Semaphore(1)))
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task

    async def test_mock_failure_is_not_hidden(self):
        with patch.object(demo, "query", AsyncMock(side_effect=ValueError("字段无效"))):
            with self.assertRaises(ValueError):
                await demo.safe_query("T4", 0, asyncio.Semaphore(1))

    async def test_semaphore_limit(self):
        # 直接观察在途任务，不用墙钟时间推断并发。
        active = 0
        maximum = 0
        semaphore = asyncio.Semaphore(2)
        original_sleep = asyncio.sleep
        async def observed(delay):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await original_sleep(0)
            active -= 1
        # 替换演示中的等待，实际调用query；如果query丢失信号量门禁会失败。
        with patch.object(demo.asyncio, "sleep", side_effect=observed):
            await asyncio.gather(*(demo.query(str(index), 0, semaphore) for index in range(5)))
        self.assertEqual(maximum, 2)

if __name__ == "__main__":
    unittest.main()
