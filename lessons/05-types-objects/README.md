# 阶段 05：类型、对象与SDK常见语法

## 使用场景

工单字段越来越多，散落字典难以表达状态。用数据类表示工单，用组合接入仓库，再理解推导式、生成器和装饰器。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 创建普通类实例，区分类、self、实例字段与组合。
- 读懂dataclass和类型标注，并指出字段校验实际在哪里执行。
- 把推导式还原成循环，解释解包与yield的执行过程。
- 将简单装饰器还原成函数赋值，确认参数和返回值如何传递。

## 前置知识与阅读顺序

先完成阶段 04 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 类、实例与组合

先只创建一个有两个字段的对象，不引入装饰器或类型标注：

```python
# class定义一种对象；__init__在初始化每个实例时保存它自己的字段。
class Ticket:
    def __init__(self, ticket_id, priority):
        self.ticket_id = ticket_id
        self.priority = priority

first = Ticket("T-1", 4)
second = Ticket("T-2", 2)
print(first.priority)
print(second.priority)
```

输出依次为4、2。执行class语句得到类对象Ticket；调用Ticket时产生实例，并运行初始化过程。`self`表示正在初始化的那个实例，所以给first设置的priority不会自动变成second的priority。`self.priority`是对象上的属性，单独的`priority`是本次调用接收的参数。两个名字写法相似，位置却不同。


字典`{"ticket_id":"T-1","priority":4}`可以装字段，但每处都要记住键名和访问方式。类把字段与围绕字段的行为放在一起：`Ticket("T-1", 4)`创建一个工单实例，`ticket.priority`读取它的优先级。`TicketRepository`把工单列表保存为`self.tickets`并提供`find`，这是组合：仓库“拥有/使用”工单对象，而不是“是一种”工单。

在[普通类示例](examples/01_class_composition.py)里，`__init__(self, ticket_id, priority)`在创建实例时执行；`self`是当前实例，所以`self.ticket_id = ticket_id`把传入值保存在对象上。`repository.find("T-1")`返回工单对象，随后`.priority`得到4；查找不到时显式返回`None`。构造仓库时`list(tickets)`复制外层列表，但列表里的Ticket对象仍是同一批对象。

Java对照：`Ticket`接近普通Java对象，`TicketRepository`接近持有DAO/实体集合的服务。Python写出`self`参数，调用者不传它；实例字段也无需先声明在类体里。

<details><summary>先预测：find("T-9")返回None后，立即写 find("T-9").priority 会怎样？</summary>

会因`None`没有`priority`属性而抛`AttributeError`。调用者应先检查是否找到对象；查无记录是正常业务结果，不一定要抛异常。
</details>

### 2. 数据类与类型标注

普通类的`__init__`常只负责把参数赋给字段。`@dataclass`为数据承载类生成常见方法，演示里的`Ticket`因此可以写成`Ticket("T-2", 3)`，并得到可读的对象表示。`ticket_id: str`和`priority: int`说明开发者预期的数据类型，但Python运行时仍允许传入不合规值。

dataclass生成的初始化方法赋值完成后，会调用`__post_init__`。这里先用`isinstance(ticket_id, str)`确认类型，再调用`.strip()`去掉首尾空白并检查非空；`priority`要求`type(value) is int`且范围1—5。用`type(...) is int`是因为`bool`是`int`的子类：`isinstance(True, int)`为真，但工单优先级`True`没有业务意义。

Java对照：Java有编译期类型检查；Python类型标注不自动做运行时校验。dataclass像便捷DTO，但不是自动校验器，也默认可变。

<details><summary>先预测：Ticket("T-3", True)会通过priority的isinstance(value, int)检查吗？</summary>

会，因为`bool`继承自`int`；本例特意用`type(value) is int`拒绝True和False。只检查注解不会阻止该输入。
</details>

### 3. 推导式、解包与生成器

先写熟悉的循环，再与紧凑写法对照。下面的两个列表内容相同：

```python
# 普通写法先建立空列表，再逐项判断和追加。
priorities = [5, 2, 4]
selected = []
for priority in priorities:
    if priority >= 4:
        selected.append(priority)

# 推导式只是把同一过程写进一行；不是先执行最左侧表达式。
compact = [priority for priority in priorities if priority >= 4]
print(selected)
print(compact)
```

两次输出都是`[5, 4]`。阅读推导式时先看for的输入，再看if筛选，最后看最左侧留下什么；不能按书写位置误以为左边的priority在循环绑定前就被求值。等普通循环能解释清楚，再用推导式减少重复语法。


短小的数据转换可写成列表推导式`[表达式 for 名称 in 可迭代对象 if 条件]`。示例按顺序读取工单元组，只对priority至少4的行保留ID，结果是新列表。`first_id, first_priority = tickets[0]`把二元组的两个值分别绑定到两个名字；左右数量不相等会抛`ValueError`。

生成器函数里出现`yield`后，调用`urgent_tickets(tickets)`先返回生成器对象，函数体不会立即跑完。`for`每次请求一个值，函数运行到`yield`时交出当前工单并暂停，下一轮再从暂停处继续查找。它可以逐条处理大集合而不建立完整结果列表，但同一个生成器消费完后已经耗尽。

Java对照：列表推导式接近Stream的filter/map后收集成List；生成器是惰性迭代，和一次性迭代器更接近，不能假定重复遍历会重放。

<details><summary>先预测：tickets有3项，只满足urgent条件的有2项。推导式结果长度是多少？同一个生成器list两次呢？</summary>

推导式创建的列表长度是2。若把同一个生成器先`list(generator)`一次，第二次通常得到空列表，因为第一次迭代已经把它消费完。
</details>

### 4. 装饰器

装饰器是一个接收函数并返回另一个函数的函数。定义`@log_call`下面的`ticket_count`时，Python先建立原函数对象，再执行`ticket_count = log_call(ticket_count)`，名称最终指向包装器。调用新函数时，包装器先打印函数名，再把参数转交给原函数，最后把原函数返回值交回调用者。

`*args`把收到的位置参数收集为tuple，`**kwargs`把关键字参数收集为dict；在调用`function(*args, **kwargs)`时，星号反过来展开参数。`return function(...)`不能漏掉，否则原函数算出的2会丢失，调用者只得到`None`。`@wraps(function)`让包装器保留原函数的名称等元信息，便于调试。

Java对照：装饰器会改变函数名当前绑定到的可调用对象；Java注解通常只是元数据，运行逻辑需框架反射或编译插件另行处理。本课要求能读懂常见包装器，不要求一开始写复杂装饰器。

<details><summary>先预测：删掉wrapper里的return，ticket_count(["T-1"])会返回几？</summary>

返回`None`。包装器仍会调用原函数，但没有把原函数结果返回。日志出现不代表被包装的业务函数结果仍被保留。
</details>

## 分小节学习与预测题

先运行短示例，再读下方综合演示。每次先预测输出，执行后解释变量的新旧值和调用顺序。以下命令均从项目根目录运行；使用项目虚拟环境时把`python`替换为`.\.venv\Scripts\python.exe`。

1. [普通类与组合](examples/01_class_composition.py)：运行 `python lessons/05-types-objects/examples/01_class_composition.py`，输出`4`。先预测仓库保存的是Ticket还是Ticket的子类，再追踪`TicketRepository([Ticket(...)])`如何把对象放进`self.tickets`。把ID改成`T-9`，观察`find`明确执行`return None`。
2. [类型标注与数据类](examples/02_types_dataclass.py)：运行 `python lessons/05-types-objects/examples/02_types_dataclass.py`，先看到合法实例。再把priority改成`True`或6：对象构造进入`__post_init__`后抛`ValueError`。`ticket_id`先确认是字符串再调用`strip`，避免非字符串输入先触发`AttributeError`。
3. [推导式与解包](examples/03_comprehension_unpacking.py)：运行 `python lessons/05-types-objects/examples/03_comprehension_unpacking.py`，先预测T-1与T-3会入选，再对照输出。把首项换成三元素元组，观察二个变量不能解包三个值。
4. [生成器](examples/04_generators.py)：运行 `python lessons/05-types-objects/examples/04_generators.py`，只打印T-1。调用函数时先得到生成器；`for`要值时函数才运行到`yield`，暂停后继续查T-2。先把返回值改成列表，比较全部物化与逐条产出的差异。
5. [装饰器阅读](examples/05_decorators.py)：运行 `python lessons/05-types-objects/examples/05_decorators.py`，依次打印调用提示和数量2。把代码改写为`ticket_count = log_call(ticket_count)`可见`@`语法的真实顺序；再暂时删除wrapper里的return，预测并确认返回值为何丢失。初学要求读懂和使用，不要求编写复杂装饰器。

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

1. Python读取装饰器定义时只创建函数；读到`@dataclass`时处理`Ticket`类，生成初始化等方法。它不会自动替注解检查输入。
2. 创建`Ticket("T1", 5)`时，生成的初始化方法依次绑定字段，随后`__post_init__`验证：ID非空，priority是1—5的严格整数。若改成True，`type(True) is int`为假，构造在边界处停止。
3. `Repository`执行`list(tickets)`产生新的外层列表；这只复制容器。若随后修改原列表的结构，仓库的列表不变；若修改其中共享Ticket对象的字段，两个列表看见的是同一个对象。
4. 调用`repository.urgent()`时，装饰器包装器打印“调用：urgent”，再调用原方法。由于原方法含`yield`，此时获得的是生成器，循环体尚未完成。
5. 列表推导式开始消费生成器。T1优先级5满足条件，于是yield交出T1；恢复后检查T2优先级2并跳过。推导式得到`['T1']`。随后二元组`('T1', 5)`被拆到两个变量，数量必须对应。

失败反例：把生成器当成列表直接打印，只会看到生成器对象描述；把解包右边换成三个值会报错；给注解`priority: int`却不写`__post_init__`，也不会自动拒绝字符串或True。

## Java 对照

Java的POJO/record都能承载工单数据；Python dataclass少写构造与展示代码，但本课对象仍可变，且注解不会运行时校验。Python实例方法显式写`self`，调用者只写`repository.urgent()`，解释器把当前实例传入。Java Stream通常显式终结为List；Python推导式立即建列表，生成器则在消费时逐项执行。Java注解是元数据，Python装饰器会把函数名重新绑定到包装函数。

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
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 05`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
