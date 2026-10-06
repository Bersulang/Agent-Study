# 可选：pytest、格式与类型检查

默认演示和unittest无第三方依赖。本目录提供可选开发工具基线，并锁定版本便于复现。
这些是已发布的教学基线，不声称是最新版本；需要网络安装，本次未安装、未执行这三个工具。

从项目根目录执行，已有 `.venv` 可直接使用，不必激活或更改执行策略：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/06-async-testing/integrations/dev-requirements.txt
.\.venv\Scripts\python.exe -m pytest lessons/06-async-testing/tests -v
.\.venv\Scripts\python.exe -m ruff format --check lessons/06-async-testing/examples
.\.venv\Scripts\python.exe -m mypy --check-untyped-defs lessons/06-async-testing/examples/demo.py
```

`-r`读取依赖清单；包只安装进该解释器的环境。
pytest可运行已有unittest案例，提供更易读断言、参数化与fixture；不需要重写本课测试才能开始。
fixture提供每个测试可控资源；Mock替换外部调用，它不是性能或模型质量保证。
ruff format --check只检查格式，不修改文件；移除--check才会改写，请理解差异。
mypy做静态类型检查，不执行程序，也不自动验证网络JSON。
未标注函数默认检查有限；--check-untyped-defs检查其函数体，但缺标注仍限制推断能力。

## 小例子：pytest参数化

以下示例只说明新语法，默认课程用unittest，不要求复制执行：

```python
import pytest

# 装饰器把两组输入交给同一测试，pytest负责重复调用。
@pytest.mark.parametrize("value,expected", [(1, 2), (3, 4)])
def test_increment(value, expected):
    assert value + 1 == expected
```

`assert`在条件不成立时抛AssertionError；它适合测试，不作为生产输入校验，因为优化模式可禁用断言。
`pytest.mark.parametrize`是第三方装饰器，不是Python内置语法。
正式工程需把工具配置放入pyproject.toml并限定检查范围，不能一上来对整个课程要求同一种复杂配置。

## 官方来源

- [pytest支持unittest](https://docs.pytest.org/en/stable/how-to/unittest.html)
- [Ruff格式工具](https://docs.astral.sh/ruff/formatter/)
- [mypy入门](https://mypy.readthedocs.io/en/stable/getting_started.html)

2026-10-06核查上述官方文档。可选工具未执行，已执行的是本课标准库unittest回归。
