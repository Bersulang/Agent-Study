"""参考答案：完成练习后再阅读；展示正常、边界及失败证据。"""
from pathlib import Path
import runpy

# 使用文件位置定位同阶段实现，不依赖当前终端目录，也不触发演示入口。
api = runpy.run_path(str(Path(__file__).resolve().parents[1] / "examples/demo.py"))

buckets = {tenant: api["TokenBucket"](1, 1) for tenant in ["A", "B"]}
assert buckets["A"].allow(0) and not buckets["A"].allow(0)
assert buckets["A"].tokens == 0 and buckets["B"].allow(0)
assert buckets["A"].allow(1)  # 一秒补回一个额度。
for now, cost in [(1, -1), (0, 1)]:
    before = (buckets["A"].tokens, buckets["A"].last)
    try:
        buckets["A"].allow(now, cost)
    except ValueError:
        assert (buckets["A"].tokens, buckets["A"].last) == before
        print("非法成本或倒退时钟：拒绝且状态不变")
    else:
        raise AssertionError("非法输入不能扣额度")
# 零容量桶无意义，直接拒绝；零剩余额度则是合法耗尽状态，能随后恢复。
try:
    api["TokenBucket"](0, 1)
except ValueError:
    print("零容量配置：拒绝")
latencies = [10] * 18 + [200, 400]
print("固定20条教学样本，平均/p95：", sum(latencies)/len(latencies), api["percentile"](latencies,.95))
assert api["percentile"](latencies, .95) == 200
