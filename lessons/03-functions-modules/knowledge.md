# 阶段03知识整理：函数、作用域与模块

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 函数与返回值

定义：def定义可重复调用的行为；参数接收输入，return将结果交给调用者。

使用：select(tickets, minimum=4)返回列表；print仅展示，不可替代return。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 默认参数与作用域

定义：默认参数在定义函数时计算一次；局部变量仅在本次调用中使用。

使用：tags=None后在函数内部创建列表，避免默认[]被多次调用共享。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 模块与执行入口

定义：一个.py文件是模块；import首次导入时执行顶层代码。

使用：__name__ == "__main__"区分直接运行和导入；路径所在目录影响模块查找。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 位置与关键字参数

定义：位置参数按顺序匹配；关键字参数按名字匹配，便于表达可选策略。

使用：select(records, minimum=5)比select(records,5)更清楚，参数名变更会影响调用方。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 执行与失败路径

解释器执行from rules import，从同目录rules.py导入函数；模块只定义函数，不打印。

直接运行时入口条件为真，调用main；导入时不调用main。

minimum通过关键字绑定到4，result是select的局部变量。

return结束函数，调用者拿到列表；没有return时隐式得到None。

两次add_tag各自新建列表，所以第二次没有urgent。

## Java迁移

Python函数无需放进Java类；模块可类似工具类或包中单元。Python没有Java式同名重载，后一次def同名函数会覆盖前者。参数默认值与Java重载写法不同。

## 工程应用

服务端把I/O和纯业务规则分开，规则函数便于测试。包是模块的组织方式，传统包可用__init__.py；本课直接运行单文件，后续按稳定边界拆包。

## 复习与验证

先解释概念，再完成[独立练习](exercises/README.md)。

保留真实运行记录；参考答案能运行不代表你已掌握。

[官方来源](https://docs.python.org/zh-cn/3.12/tutorial/)

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
