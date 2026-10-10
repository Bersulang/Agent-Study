# 阶段05知识整理：类型、对象与SDK常见语法

关联课程：[讲义](README.md)；例子：[综合演示](examples/demo.py)、[普通类与组合](examples/01_class_composition.py)、[类型标注与数据类](examples/02_types_dataclass.py)、[推导式与解包](examples/03_comprehension_unpacking.py)、[生成器](examples/04_generators.py)、[装饰器](examples/05_decorators.py)。

## 组合和继承有什么区别？

看[普通类示例](examples/01_class_composition.py)：Repository保存Ticket实例，并调用其字段，这叫“仓库有工单”；它不是工单的一种，所以无需继承。`__init__`在`Ticket("T-1", 4)`时给当前对象写入字段；查找成功返回对象，失败显式`return None`。在Java里这接近Repository持有POJO/实体集合。

## dataclass能替我验证类型吗？

不能。`@dataclass`根据`ticket_id: str`和`priority: int`生成构造方法，但Python不会据此拒绝`Ticket(9, "high")`。`__post_init__`才是真正的校验位置：先`isinstance(ticket_id, str)`再`.strip()`；优先级检查`type(priority) is int`并要求1—5。因为`bool`是`int`子类，`isinstance(True, int)`为真，而严格type比较为假。Java有编译期类型检查，Python注解本身没有这个保证。

## 推导式、解包和生成器的结果何时出现？

推导式对输入立即迭代并创建列表；示例从`[("T-1",5),("T-2",2),("T-3",4)]`得到`["T-1","T-3"]`。解包把第一个二元组的两项绑定给两个名称；三项对两个名称会失败。含`yield`的函数调用先返回生成器对象，迭代器请求下一项时才继续运行函数体，所以它能在数据量大时避免一次创建全部结果。它是一次性迭代器，耗尽后不会自动重置。

## 装饰器会不会改变函数结果？

`@log_call`等价于`ticket_count = log_call(ticket_count)`。包装器先打印“调用 ticket_count”，再执行原函数并返回其结果2。`*args`和`**kwargs`在定义包装器时分别收集位置和关键字实参，调用原函数时再展开。漏掉`return function(...)`会让调用者只拿到`None`；`@wraps`保留原函数的名称等信息。Java注解通常是元数据，Python装饰器则实际替换名字绑定的函数对象。

## 执行与失败路径

综合演示先经`@dataclass`生成Ticket构造方法；实例构造随后跑`__post_init__`。Repository复制列表外壳，却保留内部对象引用。调用`urgent()`时包装器先输出调用提示；原函数由于含`yield`返回生成器，只有列表推导式开始取值时才筛选T1并跳过T2。最后二元组拆成ID与priority。分别改变外层列表和Ticket字段，可以区分浅拷贝与对象共享。

## Java迁移

Java record可以表达不可变数据，Python dataclass默认仍可变；`self`显式写在方法签名中，调用时由解释器传入。推导式类似Stream转换后立即收集，生成器更像惰性的一次性迭代器。装饰器与Java注解不等价：一个替换可调用对象，一个通常只是元数据。

## 工程应用

SDK常见数据类、类型标注、迭代器与装饰器。阅读接口时区分“静态说明”和“运行时保证”；把仓库与工单组合在一起，比为每种仓库角色建立继承树容易替换和测试。

## 复习与验证

先预测：`Ticket("  ", 3)`与`Ticket("T-1", True)`分别在哪里拒绝？列表推导式遇到priority 2时会生成什么？再完成[独立练习](exercises/README.md)，把字典列表转换为经校验的Ticket实例并筛出高优先级。独立练习是你需要实现的契约；solutions仅供完成后对照。

[官方来源](https://docs.python.org/zh-cn/3.12/library/dataclasses.html)

## SDK语法逐项读法

`class Ticket:`创建类；`self.id`是当前实例字段；`Ticket("T1", 5)`创建实例。
`id: str`、`priority: int`是类型标注，运行时仍必须显式检查。
`@dataclass`在类定义后处理类；`@traced`在方法定义后替换方法。
`*args`收集位置参数为元组，`**kwargs`收集关键字参数为字典；调用时相反地展开。
`[ticket.id for ticket in repository.urgent()]`等价于创建空列表后循环append。
`[(t.id,t.priority) for t in tickets if t.priority >= 4]`在每轮先筛选再生成元素。
`yield ticket`产生一个值并暂停；函数包含yield时调用返回生成器，而非立即执行整段循环。
生成器通常只能消费一次；反复list同一个生成器，第二次可能为空。
