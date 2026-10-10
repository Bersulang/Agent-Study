# 阶段02复习：从输出反推对象与控制流程

这份文件用于学完[讲义](README.md)后复习，不替代首次阅读。每个问题先自己解释，再展开核对。例子均可与[完整演示](examples/demo.py)中的对象变化对应起来。

## 1. 两个名字绑定同一个值，为什么有时互不影响？

```python
# 改变名字的绑定，不会把原整数对象改成另一个整数。
a = 4
b = a
a = 7
print(b)
```

<details>
<summary>查看解释</summary>

输出4。执行`b = a`时，右侧求值得到4，b因此绑定到4；之后`a = 7`只重新绑定a。赋值并没有让b保存一个持续读取a的公式。整数不可变，名字可以重新绑定，这两件事并不矛盾。

</details>

把整数换成列表后，要看具体执行的是哪种操作：`a = []`重新绑定名字，`a.append(...)`修改已有对象。Java中的引用赋值也不自动复制集合，但不要用Java基本类型变量的模型去解释所有Python对象。

## 2. 为什么两个方括号可以连着写？

```python
# 先在列表里按位置找字典，再在字典里按键找值。
tickets = [{"id": "T1", "status": "open"}]
print(tickets[0]["status"])
```

先求`tickets[0]`得到第一张工单字典，再求这个字典的`["status"]`得到`open`。索引0属于列表，键`"status"`属于字典。若列表为空，第一个访问会失败；若字典没有status键，第二个访问会失败。错误位置帮助你区分输入结构的哪一层不符合预期。

## 3. “不是closed”与“是open”有什么不同？

假设`status = "assigned"`。`status != "closed"`为True，`status == "open"`为False。因此筛选条件必须来自当前业务要求：演示筛未关闭高优先级记录，练习只统计open记录。

`and`在本课组合两个比较结果。左边为False就短路，不再计算右边。不要把本课的布尔用法泛化成“and总返回布尔值”；Python中它一般返回某个操作数。

## 4. 为什么结果容器要先创建，再开始循环？

考虑“累计到现在的所有结果”这个含义。容器放在循环前创建，后续每轮延续同一份结果；放在循环体里重新创建，则每轮把前面的累计丢掉。空输入时循环执行零次，循环前创建的空容器仍能作为返回结果。

`for ticket in tickets`把元素本身绑定给ticket，不会复制字典。`urgent.append(ticket["id"])`只追加编号；若追加整个ticket，结果会共享原记录。`append`原地修改列表，返回None，因此不要写`urgent = urgent.append(...)`。

## 5. copy隔离了哪一层？

```python
# 外层字典有两个，内层tags列表只有一个。
ticket = {"status": "open", "tags": ["网络"]}
snapshot = ticket.copy()
ticket["status"] = "assigned"
ticket["tags"].append("紧急")
print(snapshot["status"])
print(snapshot["tags"])
```

<details>
<summary>核对两次输出</summary>

先输出open，再输出`['网络', '紧急']`。给原字典的status重新放入一个字符串，不影响副本中的键；tags仍共享一个列表，append会被两边看到。“是否复制过”不是足够精确的问题，要问“哪个容器新建了，里面的对象是否还共享”。

</details>

元组也只能保证自己的元素位置不能重新设置，不保证嵌套列表不可变。用两个字符串组成元组时，可以得到简单稳定的字段组合；不要因此把元组当作通用深快照。

## 6. 去重为什么不能代替计数？

`set`只保留成员是否存在，IT出现一次和十次都只保存一个IT。部门计数需要字典将部门映射到数量。`counts.get(department, 0)`读取旧值或默认值，不负责写入；赋值语句才把加一后的值保存起来。

展示集合时可以用`sorted`得到新列表。不要为了稳定展示而改动“筛选结果需保留输入顺序”的业务要求；两种输出的顺序约定并不相同。

## 7. print和return可以互换吗？

不可以。`print`把信息显示到终端；`return`把结果交给调用者并结束当前函数。自动检查器调用`solve(data)`并检查返回值，不能从“终端看起来对了”推断返回值也正确。

本阶段只借用现成函数骨架，完整调用与作用域模型见[阶段03](../03-functions-modules/README.md)。遇到`NotImplementedError`表示骨架还没有被你的实现替换，属于明确的待完成状态。

## 回到独立练习

打开[练习说明](exercises/README.md)。给自己准备一组至少包含open、closed、assigned的记录，先预测编号列表、部门计数和原始数据是否变化，再运行校验。解释错误比背术语更重要，无需手填运行日志。

[Python数据结构教程](https://docs.python.org/zh-cn/3.12/tutorial/datastructures.html)用于查语法；[Composing Programs可变数据](https://composingprograms.com/pages/24-mutable-data.html)用于继续练习对象关系分析。
