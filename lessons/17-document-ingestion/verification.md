# 默认验证记录

2026-10-06；Python 3.12.10；工作目录为项目根目录。

核心行为测试先在接口显式抛出NotImplementedError时执行，确认尚未实现；实现后复跑通过。集成契约测试不等于实际模型质量测试。

## 执行命令

```powershell
python lessons\17-document-ingestion\examples\demo.py
```

退出码：0

```text
policy.md 1 0 # 报销规则
出差交通费需要发票。
policy.md 2 0 审批后才能付款。
```

## 执行命令

```powershell
python lessons\17-document-ingestion\solutions\solution.py
```

退出码：0

```text
{'chunks': [{'text': '需要发票', 'locations': [('a.md', 1), ('b.md', 1)]}], 'errors': [{'source': 'scan.pdf', 'error': '没有可提取文字，需要检查文本层或OCR'}]}
```

## 执行命令

```powershell
python -m unittest discover -s lessons\17-document-ingestion\tests -v
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
python lessons\17-document-ingestion\examples\structured_files.py
```

退出码：0

```text
[{'heading': '交通费', 'line': 2, 'text': '需要发票'}, {'heading': '住宿费', 'line': 4, 'text': '限额800'}]
[{'row': 2, 'department': 'ENG', 'limit': 800}, {'row': 3, 'department': 'HR', 'limit': 500}]
```

默认案例与本地行为测试通过不代表学员掌握；外部集成验证范围见integrations/README.md与integrations/verification.md（如有）。
