# 阶段50参考答案覆盖说明

完成练习后再阅读与运行；这些参考代码不替代学员提交与能力验收。

solution.py发布两个合法版本，分别拒绝低质量与安全违规版本并断言旧版本和版本列表未改变；旧任务版本固化，最后安全回滚。course-checks.yml是需复制到CI目录的参考配置，不会自行部署。生产人工审查：身份权限扩大、模型与索引数据变化、数据库迁移兼容性、预算改变、回滚/补偿方案。

从项目根目录执行：

```powershell
python lessons/50-version-release/solutions/solution.py
python -m unittest discover -s lessons/50-version-release/tests -v
```

先预测业务状态，再检查断言与失败类型。示例复用同课函数，新增验证案例负责证明扩展规则；tests通过不能代表你的practice已完成。
