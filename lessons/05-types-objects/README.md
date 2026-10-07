# 阶段 05：类型、对象与SDK常见语法

## 使用场景

工单字段越来越多，散落字典难以表达状态。用数据类表示工单，用组合接入仓库，再理解推导式、生成器和装饰器。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 04 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 类、实例与组合

类描述对象结构；实例拥有具体字段；组合表示一个对象使用另一个对象服务。

用途与例子：Ticket代表一条工单；Repository保存Ticket，不必继承Ticket。

### 2. 数据类与类型标注

@dataclass生成初始化等常见方法；field: str说明预期类型，不自动验证。

用途与例子：__post_init__显式拒绝空id与越界priority；bool是int子类，严格整数可用type(value) is int。

### 3. 推导式、解包与生成器

推导式构造容器；解包将多个值绑定变量；yield每次产生一个值并暂停。

用途与例子：[t.id for t in tickets]生成完整列表；生成器逐条处理，避免全量物化。

### 4. 装饰器

装饰器接收函数并返回替代函数；@decorator等价于func=decorator(func)。

用途与例子：wraps保存原函数元信息；包装器用*args/**kwargs传递位置/关键字参数。

## 分小节学习与预测题

先运行短示例，再读下方综合演示。每次先预测输出，执行后解释变量的新旧值和调用顺序。以下命令均从项目根目录运行；使用项目虚拟环境时把`python`替换为`.\.venv\Scripts\python.exe`。

1. [普通类与组合](examples/01_class_composition.py)：运行 `python lessons/05-types-objects/examples/01_class_composition.py`。`__init__`在创建对象时设置字段；`self`指当前工单实例。找不到工单时执行示例里的显式`return None`。
2. [类型标注与数据类](examples/02_types_dataclass.py)：运行 `python lessons/05-types-objects/examples/02_types_dataclass.py`。dataclass生成常见构造方法；`__post_init__`随后显式校验。试传`True`，观察它被拒绝，类型标注本身不做运行时校验。
3. [推导式与解包](examples/03_comprehension_unpacking.py)：运行 `python lessons/05-types-objects/examples/03_comprehension_unpacking.py`。推导式逐项筛选并生成新列表，不改原列表。先预测字段数不匹配时的解包异常，再试三元素元组。
4. [生成器](examples/04_generators.py)：运行 `python lessons/05-types-objects/examples/04_generators.py`。执行到`yield`会产出一项并暂停；下次迭代从暂停位置继续。生成器耗尽后不能自动从头开始。
5. [装饰器阅读](examples/05_decorators.py)：运行 `python lessons/05-types-objects/examples/05_decorators.py`。`@log_call`等价于定义后执行`ticket_count = log_call(ticket_count)`；`*args/**kwargs`转交参数，`return`把结果交回调用者。初学要求读懂和使用，不要求编写复杂装饰器。

Java对照：普通类接近POJO，dataclass像便捷DTO但不自动校验；Java有编译期类型检查，Python类型标注不自动执行运行时校验。装饰器会包装并替换函数对象，和仅供框架读取的Java注解不同。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/05-types-objects/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
调用：urgent
紧急：['T1']；解包：T1/5
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""类型标注服务于阅读；校验必须显式执行。"""
from dataclasses import dataclass
from functools import wraps

def traced(function):
    # @wraps保留名称，包装器把调用转交给原函数。
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"调用：{function.__name__}")
        return function(*args, **kwargs)
    return wrapper

@dataclass
class Ticket:
    id: str
    priority: int

    def __post_init__(self):
        # dataclass不会自动验证类型；拒绝bool充当整数优先级。
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id不能为空")
        if type(self.priority) is not int or not 1 <= self.priority <= 5:
            raise ValueError("priority必须是1到5的整数")

class Repository:
    def __init__(self, tickets):
        self.tickets = list(tickets)

    @traced
    def urgent(self):
        for ticket in self.tickets:
            if ticket.priority >= 4:
                # yield暂停在这里，下次迭代继续for。
                yield ticket

if __name__ == "__main__":
    repository = Repository([Ticket("T1", 5), Ticket("T2", 2)])
    identities = [ticket.id for ticket in repository.urgent()]
    identity, priority = ("T1", 5)
    print(f"紧急：{identities}；解包：{identity}/{priority}")
```

## 代码执行过程与逐段解释

1. 装饰器函数定义后，@dataclass处理Ticket，生成__init__等方法。
2. Ticket("T1",5)先赋字段，再调用__post_init__，错误输入在对象边界拒绝。
3. Repository复制外层列表，但内部Ticket对象仍共享，不能假设深复制。
4. 调用urgent先执行wrapper；返回生成器对象，尚未遍历函数体。
5. 列表推导式开始迭代生成器，yield产出T1；元组解包必须元素数匹配。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

数据类接近Java DTO/record用途，但默认并非不可变；需要frozen=True才禁止通常的字段赋值。Pythonself显式出现在方法参数中，调用时自动传入。装饰器与Java注解不同：装饰器真实替换对象。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 标注priority:int却传字符串：标注不强制，边界必须校验。
- 把生成器打印成结果：显示对象地址，应用list或for消费。
- 解包数量错误：核查返回结构，不要随意增加占位变量。
- 装饰器忘记return：调用得到None，需返回原函数结果。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data为字典列表，构造经过校验的Ticket并返回priority>=4的(id,priority)元组列表。每条要求id非空、priority为1—5整数，拒绝True。输入不变。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/05-types-objects/exercises/practice.py
python lessons/05-types-objects/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

SDK常见数据类、类型标注、迭代器与装饰器。读接口时区分“静态说明”和“运行时保证”；组合优先于为每个角色层层继承。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/dataclasses.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

## SDK语法逐项读法

`class Ticket:`创建类；`self.id`是当前实例字段；`Ticket("T1", 5)`创建实例。
`id: str`、`priority: int`是类型标注，运行时仍必须显式检查。
`@dataclass`在类定义后处理类；`@traced`在方法定义后替换方法。
`*args`收集位置参数为元组，`**kwargs`收集关键字参数为字典；调用时相反地展开。
`[ticket.id for ticket in repository.urgent()]`等价于创建空列表后循环append。
`[(t.id,t.priority) for t in tickets if t.priority >= 4]`在每轮先筛选再生成元素。
`yield ticket`产生一个值并暂停；函数包含yield时调用返回生成器，而非立即执行整段循环。
生成器通常只能消费一次；反复list同一个生成器，第二次可能为空。
