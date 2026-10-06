# 阶段47参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py读取合法文件，拒绝../、绝对路径、目录与非允许扩展名；URL拒绝HTTP、内嵌用户名与非允许端口。DNS需解析后IP与出口代理校验，重定向每跳验证目的地；TOCTOU需隔离或不可变挂载。

从项目根目录执行：

```powershell
python lessons/47-injection-sandbox/solutions/solution.py
python -m unittest discover -s lessons/47-injection-sandbox/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。
