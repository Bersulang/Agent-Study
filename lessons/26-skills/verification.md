# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\26-skills\examples\demo.py
```

退出码：0

```text
['report']
{'version': '1.0', 'trigger': '报告', 'permission': 'read', 'instructions': '读取工单；汇总数量；使用中文模板；标注来源。'}
```

## 执行命令

```powershell
python lessons\26-skills\solutions\solution.py
```

退出码：0

```text
{'version': '1.0', 'trigger': '报告', 'permission': 'read', 'instructions': '读取工单；汇总数量；使用中文模板；标注来源。'}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\26-skills\tests -v
```

退出码：0

```text
test_boundary_and_failure (test_behavior.BehaviorTests.test_boundary_and_failure) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

## 执行命令

```powershell
python lessons\26-skills\resources\report\scripts\summarize.py
```

退出码：0

```text
{"counts": {"open": 1, "closed": 1}, "errors": [{"row": 4, "id": "T3", "reason": "invalid_status"}]}
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
