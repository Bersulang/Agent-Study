# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\20-knowledge-lifecycle\examples\demo.py
```

退出码：0

```text
updated
updated
2
{}
```

## 执行命令

```powershell
python lessons\20-knowledge-lifecycle\solutions\solution.py
```

退出码：0

```text
2 {'new': {'text': '新政策', 'digest': '71eedf97d7d5765849fd7ed28a5d2b13ff211ce9a9cc55733b2ec2c1c2ce89a9', 'version': 1, 'expires': None}}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\20-knowledge-lifecycle\tests -v
```

退出码：0

```text
test_boundary_and_failure (test_behavior.BehaviorTests.test_boundary_and_failure) ... ok
test_expiry_boundary_and_metadata_change (test_expiry.ExpiryTests.test_expiry_boundary_and_metadata_change) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
