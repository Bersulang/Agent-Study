# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\28-mcp-local\examples\demo.py
```

退出码：0

```text
{'tools': {'get_ticket': {'description': '查询工单', 'required': ['ticket_id']}}}
{'found': True, 'ticket': {'status': 'open', 'title': '登录失败'}}
```

## 执行命令

```powershell
python lessons\28-mcp-local\solutions\solution.py
```

退出码：0

```text
{'ok': False, 'error': {'code': 'INVALID_REQUEST', 'message': '不支持的方法'}}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\28-mcp-local\tests -v
```

退出码：0

```text
test_boundary_and_failure (test_behavior.BehaviorTests.test_boundary_and_failure) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
