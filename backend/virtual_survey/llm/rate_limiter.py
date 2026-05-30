"""限流器实现"""

import asyncio
import time
from typing import Dict


class RateLimiter:
    """令牌桶限流器"""

    def __init__(self, rate: float, capacity: int):
        """
        初始化限流器

        Args:
            rate: 令牌生成速率（个/秒）
            capacity: 令牌桶容量
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """获取一个令牌"""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_time = now

            if self.tokens < 1:
                # 计算需要等待的时间
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
                self.last_time = time.monotonic()
            else:
                self.tokens -= 1


class TokenBucketRateLimiter:
    """令牌桶限流器（支持多个桶）"""

    def __init__(self):
        self._buckets: Dict[str, RateLimiter] = {}

    def create_bucket(self, name: str, rate: float, capacity: int) -> None:
        """创建令牌桶"""
        self._buckets[name] = RateLimiter(rate, capacity)

    async def acquire(self, bucket_name: str) -> None:
        """从指定桶获取令牌"""
        if bucket_name not in self._buckets:
            raise ValueError(f"Bucket '{bucket_name}' not found")
        await self._buckets[bucket_name].acquire()

    def get_bucket(self, name: str) -> RateLimiter:
        """获取令牌桶"""
        if name not in self._buckets:
            raise ValueError(f"Bucket '{name}' not found")
        return self._buckets[name]


# 全局限流器实例
rate_limiter_manager = TokenBucketRateLimiter()

# 默认创建OpenAI限流器（60请求/分钟）
rate_limiter_manager.create_bucket("openai", rate=1.0, capacity=10)
