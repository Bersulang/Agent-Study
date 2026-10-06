# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\18-basic-rag\examples\demo.py
```

退出码：0

```text
{'status': 'supported', 'answer': '报销 发票 审批', 'citations': ['policy.md#1']}
{'status': 'no_evidence', 'answer': '资料中没有足够证据', 'citations': []}
```

## 执行命令

```powershell
python lessons\18-basic-rag\solutions\solution.py
```

退出码：0

```text
{'results': [{'question': '报销', 'status': 'supported', 'answer': '报销 发票 审批', 'citations': ['policy.md#1']}, {'question': '工资', 'status': 'no_evidence', 'answer': '资料中没有足够证据', 'citations': []}], 'missing': 1}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\18-basic-rag\tests -v
```

退出码：0

```text
test_boundary_and_failure (test_behavior.BehaviorTests.test_boundary_and_failure) ... ok
test_cosine_rejects_invalid_dimensions_and_zero (test_embedding_contract.ContractTests.test_cosine_rejects_invalid_dimensions_and_zero) ... ok
test_http_request_and_response_mapping (test_embedding_contract.ContractTests.test_http_request_and_response_mapping) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.521s

OK
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
