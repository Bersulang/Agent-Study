# 阶段05知识整理：类型、对象与SDK常见语法

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 类、实例与组合

定义：类描述对象结构；实例拥有具体字段；组合表示一个对象使用另一个对象服务。

使用：Ticket代表一条工单；Repository保存Ticket，不必继承Ticket。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 数据类与类型标注

定义：@dataclass生成初始化等常见方法；field: str说明预期类型，不自动验证。

使用：__post_init__显式拒绝空id与越界priority；bool是int子类，严格整数可用type(value) is int。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 推导式、解包与生成器

定义：推导式构造容器；解包将多个值绑定变量；yield每次产生一个值并暂停。

使用：[t.id for t in tickets]生成完整列表；生成器逐条处理，避免全量物化。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 装饰器

定义：装饰器接收函数并返回替代函数；@decorator等价于func=decorator(func)。

使用：wraps保存原函数元信息；包装器用*args/**kwargs传递位置/关键字参数。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 执行与失败路径

装饰器函数定义后，@dataclass处理Ticket，生成__init__等方法。

Ticket("T1",5)先赋字段，再调用__post_init__，错误输入在对象边界拒绝。

Repository复制外层列表，但内部Ticket对象仍共享，不能假设深复制。

调用urgent先执行wrapper；返回生成器对象，尚未遍历函数体。

列表推导式开始迭代生成器，yield产出T1；元组解包必须元素数匹配。

## Java迁移

数据类接近Java DTO/record用途，但默认并非不可变；需要frozen=True才禁止通常的字段赋值。Pythonself显式出现在方法参数中，调用时自动传入。装饰器与Java注解不同：装饰器真实替换对象。

## 工程应用

SDK常见数据类、类型标注、迭代器与装饰器。读接口时区分“静态说明”和“运行时保证”；组合优先于为每个角色层层继承。

## 复习与验证

先解释概念，再完成[独立练习](exercises/README.md)。

保留真实运行记录；参考答案能运行不代表你已掌握。

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
