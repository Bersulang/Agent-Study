"""IsolatedAsyncioTestCase为异步用例提供隔离的事件循环。"""
import asyncio
import unittest


async def fetch_status():
    await asyncio.sleep(0)
    return "open"


class AsyncStatusTests(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_returns_status(self):
        self.assertEqual(await fetch_status(), "open")


if __name__ == "__main__":
    unittest.main()
