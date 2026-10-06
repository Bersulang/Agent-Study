# 阶段 03：函数、作用域与模块

## 使用场景

筛选代码被命令行和后台任务同时调用。我们把业务规则抽成函数，并让导入模块时不会自动执行演示。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 02 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 函数与返回值

def定义可重复调用的行为；参数接收输入，return将结果交给调用者。

用途与例子：select(tickets, minimum=4)返回列表；print仅展示，不可替代return。

### 2. 默认参数与作用域

默认参数在定义函数时计算一次；局部变量仅在本次调用中使用。

用途与例子：tags=None后在函数内部创建列表，避免默认[]被多次调用共享。

### 3. 模块与执行入口

一个.py文件是模块；import首次导入时执行顶层代码。

用途与例子：__name__ == "__main__"区分直接运行和导入；路径所在目录影响模块查找。

### 4. 位置与关键字参数

位置参数按顺序匹配；关键字参数按名字匹配，便于表达可选策略。

用途与例子：select(records, minimum=5)比select(records,5)更清楚，参数名变更会影响调用方。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/03-functions-modules/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
筛选：['T1']
首次标签：['urgent']
第二次标签：['review']
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""业务模块与运行入口分离；同目录rules可直接导入。"""
from rules import select, add_tag

def main():
    records = [{"id": "T1", "priority": 5}, {"id": "T2", "priority": 2}]
    print(f"筛选：{select(records, minimum=4)}")
    print(f"首次标签：{add_tag('urgent')}")
    print(f"第二次标签：{add_tag('review')}")

if __name__ == "__main__":
    main()
```

## 代码执行过程与逐段解释

1. 解释器执行from rules import，从同目录rules.py导入函数；模块只定义函数，不打印。
2. 直接运行时入口条件为真，调用main；导入时不调用main。
3. minimum通过关键字绑定到4，result是select的局部变量。
4. return结束函数，调用者拿到列表；没有return时隐式得到None。
5. 两次add_tag各自新建列表，所以第二次没有urgent。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

Python函数无需放进Java类；模块可类似工具类或包中单元。Python没有Java式同名重载，后一次def同名函数会覆盖前者。参数默认值与Java重载写法不同。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 把print结果赋给变量：得到None，应由函数return数据。
- 默认tags=[]：多次调用共享同一列表，改用None。
- import报ModuleNotFoundError：从项目根运行并核查目录；不要随意修改系统路径。
- 模块同名json.py：会遮蔽标准库json；业务文件使用有含义名称。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data包含tickets和minimum；返回按优先级降序的工单ID，原列表不变，minimum缺省为3。把业务函数与运行入口分开，并连续调用两次验证互不污染。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/03-functions-modules/exercises/practice.py
python lessons/03-functions-modules/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

服务端把I/O和纯业务规则分开，规则函数便于测试。包是模块的组织方式，传统包可用__init__.py；本课直接运行单文件，后续按稳定边界拆包。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/tutorial/)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

## 模块拆分与新语法补充

`from rules import select, add_tag` 从rules模块导入两个名称。
直接运行demo时，其所在examples目录进入模块查找路径，因此能找到同目录rules.py。
这不意味着在任意目录手动import rules都成功；文件路径与导入模块名是两种不同概念。
业务定义见 [rules.py](examples/rules.py)，导入不会调用main或产生输出。
正式包通常用包目录和 `__init__.py` 组织，通过 `python -m 包.模块` 运行。
`-m`按模块查找；本项目阶段目录带数字和连字符，本课使用文件路径运行，不把它冒充合法包名。

答案中的 `sorted(chosen, key=priority, reverse=True)` 调用priority函数获取每条排序依据。
`key=priority`传函数对象，没有圆括号；`priority(ticket)`则是真正调用函数。
`reverse=True`表示降序；sorted返回新列表，list.sort会原地改变列表并返回None。
