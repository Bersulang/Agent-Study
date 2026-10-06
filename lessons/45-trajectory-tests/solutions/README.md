# 阶段45参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py验证只读与批准写入成功，并按异常类型验证批准前写入、重复写入、撤销后写入、finished后事件四种失败。最终回答一样也不能掩盖不同轨迹。

从项目根目录执行：

```powershell
python lessons/45-trajectory-tests/solutions/solution.py
python -m unittest discover -s lessons/45-trajectory-tests/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。
