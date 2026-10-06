# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\27-langgraph\examples\demo.py
```

退出码：0

```text
{'stage': 'waiting', 'task': 'T1'}
{'stage': 'rejected', 'task': 'T1', 'approved': False}
```

## 执行命令

```powershell
python lessons\27-langgraph\solutions\solution.py
```

退出码：0

```text
{'stage': 'rejected', 'task': 'T1', 'digest': 'v1', 'approved': False}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\27-langgraph\tests -v
```

退出码：0

```text
test_boundary_and_failure (test_behavior.BehaviorTests.test_boundary_and_failure) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
