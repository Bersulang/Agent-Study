# 阶段51参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py证明两租户独立配额、耗尽与恢复；拒绝负成本与时钟倒退且状态不变；零capacity拒绝、零剩余额度允许恢复；用20条固定样本比较平均39与最近秩p95=200。不是实际负载基准。

从项目根目录执行：

```powershell
python lessons/51-capacity-cost/solutions/solution.py
python -m unittest discover -s lessons/51-capacity-cost/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。
