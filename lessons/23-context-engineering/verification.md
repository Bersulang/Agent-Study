# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\23-context-engineering\examples\demo.py
```

退出码：0

```text
{'selected': [{'id': 'rule', 'text': '必须审批', 'priority': 100, 'required': True}, {'id': 'evidence', 'text': '发票有效', 'priority': 50}], 'dropped': ['history'], 'used': 8}
```

## 执行命令

```powershell
python lessons\23-context-engineering\solutions\solution.py
```

退出码：0

```text
{'selected': [{'id': '0', 'priority': 1, 'text': "<evidence source='a.md'>需要审批</evidence>", 'role': 'data'}], 'dropped': [], 'used': 39}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\23-context-engineering\tests -v
```

退出码：0

```text
test_boundary_and_failure (test_behavior.BehaviorTests.test_boundary_and_failure) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
