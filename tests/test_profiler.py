# tests/test_profiler.py

import unittest

from profiler import profile, profile_async, profile_with_memory


class TestProfiler(unittest.TestCase):

    def test_sync_profile(self):
        @profile
        def simple_add(a, b):
            return a + b

        result = simple_add(1, 2)
        self.assertEqual(result, 3)

    def test_async_profile(self):
        import asyncio

        @profile_async
        async def async_add(a, b):
            return a + b

        result = asyncio.run(async_add(1, 2))
        self.assertEqual(result, 3)

    def test_profile_with_memory(self):
        @profile_with_memory
        def simple_add(a, b):
            return a + b

        result = simple_add(3, 4)
        self.assertEqual(result, 7)


if __name__ == "__main__":
    unittest.main()
