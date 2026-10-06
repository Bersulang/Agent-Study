# 阶段 02：变量、容器与可变性

## 使用场景

客服希望从三个工单中找出未关闭的紧急工单，同时统计部门。先学会表示数据，才能理解Agent后来传递的消息与工具参数。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 01 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 变量与对象

变量名绑定对象；赋值不是复制对象。整数、字符串通常不可变，列表与字典可变。

用途与例子：alias = tickets 后修改alias也会影响tickets；字典.copy只复制一层。

### 2. 字符串与布尔条件

字符串是一段Unicode文本；比较得到True或False，and要求两个条件都成立。

用途与例子：status != "closed" and priority >= 4筛选未关闭高优先级工单；f字符串把表达式放进{}。

### 3. 列表、字典、元组、集合

列表保留顺序；字典按键取值；元组不能重新设置元素；集合用于唯一性。

用途与例子：工单列表内放字典，(id,status)作快照，set收集部门；set无排序保证，输出前sorted。

### 4. 循环与累计

for依次把容器元素绑定到变量，if决定本轮是否追加。

用途与例子：urgent.append(ticket["id"])只记录ID，避免之后通过结果修改原工单。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/02-basic-syntax/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
紧急工单：['T1']
部门：['HR', 'IT']
原记录：assigned；快照：open
不可变字段组合：('T1', 'open')
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""从基础容器表示工单，不引入类型标注或推导式。"""
# 列表中的每个字典代表一个工单；冒号分隔键和值。
tickets = [
    {"id": "T1", "department": "IT", "priority": 5, "status": "open"},
    {"id": "T2", "department": "HR", "priority": 4, "status": "closed"},
    {"id": "T3", "department": "IT", "priority": 2, "status": "open"},
]
urgent = []
departments = set()
for ticket in tickets:
    # 用集合去重，列表保留筛选结果的输入顺序。
    departments.add(ticket["department"])
    if ticket["status"] != "closed" and ticket["priority"] >= 4:
        urgent.append(ticket["id"])
print(f"紧急工单：{urgent}")
print(f"部门：{sorted(departments)}")
# 赋值共享列表；这里只复制一层字典，字段都是不可变值。
alias = tickets
snapshot = tickets[0].copy()
alias[0]["status"] = "assigned"
print(f"原记录：{tickets[0]['status']}；快照：{snapshot['status']}")
pair = (tickets[0]["id"], snapshot["status"])
print(f"不可变字段组合：{pair}")
```

## 代码执行过程与逐段解释

1. 三个字典在列表中创建；id、status是字符串，priority是整数。
2. urgent创建独立列表；departments创建空集合，不能用{}，那是空字典。
3. for共执行三次，T2被status条件排除，T3被优先级条件排除。
4. sorted生成新的有序列表，不修改集合。
5. alias与tickets指向同一列表；修改嵌套字典影响原值，snapshot保留open。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

Java的List<Map<String,Object>>可表达相似数据，Python无需声明泛型。两者引用赋值都不自动深复制；Python元组不可变也不代表其内部列表不可变。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- KeyError：方括号要求键存在；排查字段拼写，缺失字段的业务策略应明确。
- 把==写成=：=绑定变量，==比较；if后必须有冒号。
- 集合打印次序变化：集合用于去重，展示时排序。
- 浅复制仍共享嵌套列表：如果增加tags列表，copy不能隔离其修改。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data为工单列表，返回{"open_ids": [...], "by_department": {...}}。只统计status为open的记录；部门计数、输入顺序保留；不修改输入。空列表返回空列表与空字典。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/02-basic-syntax/exercises/practice.py
python lessons/02-basic-syntax/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

Agent状态常由嵌套字典组成。共享引用会使历史消息被后来步骤篡改；先明确所有权，再选择复制或不可变建模。不要为每次读都深复制大型上下文。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/tutorial/)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

## 第一次出现的符号与语法

- `name = value` 把名字绑定到对象；不写Java的类型声明或分号。
- `[...]` 创建列表；`{"id": "T1"}` 创建字典；`ticket["id"]` 用键读取字段。
- `for ticket in tickets:` 遍历元素；冒号后必须缩进，不能省略块结构。
- `and`组合两个布尔条件；`!=`表示不相等，`>=`表示大于等于。
- `append`把一个值加到列表末尾；`add`把值放入集合，已存在时不会重复。
- `f"紧急工单：{urgent}"`在字符串内计算花括号表达式；花括号外是普通文字。
- `counts.get(department, 0)`在键不存在时用0；这不会自动往字典写键，之后赋值才写入。
- `'open'`与`"open"`都创建相同字符串；多层引号应选择不同引号避免冲突。
