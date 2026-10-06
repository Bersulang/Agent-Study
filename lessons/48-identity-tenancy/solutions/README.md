# 阶段48参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py证明同编号租户缓存隔离，并新增write_ticket：writer角色、当前tenant和可信审批动作绑定全部满足才能写。缺审批、跨租户和无writer均不改业务数据；审计无Token和正文。审批是服务端夹具，不是接受客户端授权字段；完整协议复习43。

从项目根目录执行：

```powershell
python lessons/48-identity-tenancy/solutions/solution.py
python -m unittest discover -s lessons/48-identity-tenancy/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。
