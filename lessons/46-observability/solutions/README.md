# 阶段46参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py将model与tool关联同一request_id，保留TimeoutError类型而不泄露正文；验证递归脱敏、输入输出成本与负数拒绝。每次时长不同，不把夹具时长当生产测量。

从项目根目录执行：

```powershell
python lessons/46-observability/solutions/solution.py
python -m unittest discover -s lessons/46-observability/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。
