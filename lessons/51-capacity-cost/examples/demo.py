"""手动时钟的令牌桶，避免测试靠sleep；非分布式限流器。"""
from math import ceil

class TokenBucket:
    def __init__(self, capacity, rate, now=0.0):
        if capacity <= 0 or rate <= 0:
            raise ValueError("容量与速率必须为正")
        self.capacity, self.rate = capacity, rate
        self.tokens, self.last = float(capacity), now

    def allow(self, now, cost=1):
        if cost <= 0 or now < self.last:
            raise ValueError("成本必须为正，时钟不能倒退")
        # 先补充，再截断到最大容量，避免长时间空闲产生无限额度。
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True

def percentile(values, fraction):
    if not values or not 0 < fraction <= 1:
        raise ValueError("样本不能为空，分位参数需要在(0,1]")
    ordered = sorted(values)
    return ordered[ceil(len(ordered) * fraction) - 1]

if __name__ == "__main__":
    bucket = TokenBucket(2, 1)
    print("同一时刻三请求：", [bucket.allow(0) for _ in range(3)])
    print("一秒后恢复：", bucket.allow(1))
    latencies = [10] * 18 + [200, 400]
    print("示例平均/p95：", sum(latencies) / len(latencies), percentile(latencies, 0.95))
