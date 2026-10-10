# 阶段 03：函数、作用域与模块

## 使用场景

筛选代码被命令行和后台任务同时调用。我们把业务规则抽成函数，并让导入模块时不会自动执行演示。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 区分执行def、调用函数和接收返回值三个时刻。
- 画出一次调用中参数与局部变量的绑定，解释可变默认参数为何会共享。
- 将筛选逻辑放进可复用模块，导入时不自动启动演示。
- 独立实现带默认门槛的筛选与排序，并验证不修改输入。

## 前置知识与阅读顺序

先完成阶段 02 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，并会使用变量、列表与字典；函数定义和调用会在本课从头讲解。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 函数与返回值

先用一个只有一步计算的函数观察“定义”和“调用”的区别：

```python
# 定义时给处理步骤起名，缩进中的语句暂时不会执行。
def increase(priority):
    new_priority = priority + 1
    return new_priority

# 调用时才把4交给参数priority，执行函数体并接收返回值。
answer = increase(4)
print(answer)
```

`def`后面是函数名，圆括号里的`priority`是参数，冒号后缩进的部分是函数体。执行定义时，Python建立函数对象并把名字`increase`绑定到它。执行调用时，为本次调用建立局部环境，让`priority`绑定到4，再依次计算`new_priority`、执行`return`。返回值5交给外面的`answer`，函数结束后才执行`print`。

```text
调用者的环境：increase → 函数对象；answer在调用完成后 → 5
本次调用内部：priority → 4；new_priority → 5
```

另一次`increase(8)`有自己的参数绑定，不会自动读到上次调用的4。这里的`new_priority`是函数内部的名字，外部不能直接通过它取到结果；对外提供结果要靠return。这就是为什么只学会“函数是一段代码”还不够：还要看每次调用接收了什么、在哪里保存临时值、把什么交给了外面。


想象命令行和后台任务都要筛选紧急工单。如果每个调用点都写一遍循环，门槛改动时容易漏一处。函数把“给定工单和最低优先级，返回符合条件的ID”封装成可重复调用的规则。`def select(tickets, minimum=4)`先建立函数定义；只有执行`select(...)`时，函数体才运行。

调用`select([{"id":"T1","priority":5},{"id":"T2","priority":2}], minimum=4)`时，参数`minimum`绑定到4。循环把T1加入局部`result`，跳过T2，`return result`把`["T1"]`交还给调用者。`print(result)`只把值显示到终端；如果函数只print而没有return，调用者拿到的是`None`，无法继续排序或保存。

Java对照：Python函数可直接写在模块里；Java通常把相同规则放进类的静态方法或服务对象。两者都可以把输入输出作为契约，Python不会因为函数写在模块里就自动校验输入类型。

<details><summary>先预测：把最后一行 return result 改成 print(result)，调用者会得到什么？</summary>

调用者得到`None`。终端可能看见列表，但展示和返回是两件事；后续代码若写`sorted(select(...))`会因`None`不可迭代而失败。
</details>

### 2. 默认参数与作用域

先看一个故意写错的版本。运行时注意两次调用之间是否残留了数据：

```python
# 反例：默认列表只在定义函数时创建一次，多个调用会共用它。
def collect(label, labels=[]):
    labels.append(label)
    return labels

print(collect("第一次"))
print(collect("第二次"))
```

第一行是`['第一次']`，第二行是`['第一次', '第二次']`。函数体看起来每次都很短，却没有创建新的默认列表。即使参数名是局部名字，它指向的对象也可能被多次调用共享。“局部变量”不等于“里面的对象一定独立”。


参数默认值在执行`def`时求值一次，而不是每次调用时重新创建。若写`def add_tag(name, tags=[])`，两个未传`tags`的调用会共享同一个列表；第一次追加`urgent`后，第二次就会意外看到它。

本课的`add_tag(name, tags=None)`把“没有给标签列表”表示为`None`。当本次没有传入列表时，函数会执行`tags = []`，所以两次省略该参数的调用分别得到`["urgent"]`和`["review"]`。显式传入列表时，代码先用`list(tags)`复制外层列表，再追加新标签；调用者原列表不变。`tags`和`result`都是局部变量，但它们引用的对象是否共享，取决于对象是每次新建还是从调用者传入。

Java对照：Java常通过重载方法或`null`表达可选参数；Python用默认值更紧凑，但可变对象（list、dict、set）不应直接当默认值。

<details><summary>先预测：执行 add_tag("review", ["urgent"]) 后，传入的列表会变成什么？</summary>

仍是`["urgent"]`。函数复制了列表并返回新列表`["urgent", "review"]`；若删掉`list(tags)`，就会修改调用者传入的对象。
</details>

### 3. 模块与执行入口

一个`.py`文件可以作为模块被导入。导入时，解释器会执行模块顶层语句，因此顶层写文件、打印或发请求会让“仅仅导入”产生副作用。`rules.py`只定义`select`和`add_tag`，导入它不会打印。

`demo.py`中的`if __name__ == "__main__":`是入口保护：直接运行该文件时条件成立并调用`main()`；测试导入`demo`时，条件不成立，演示不会自动启动。直接按文件路径运行时，Python把脚本所在的`examples`目录放入模块搜索位置，所以`from rules import ...`能找到同目录文件；这不意味着从任意目录裸写`import rules`都能成功。

Java对照：这类似把可复用逻辑放在类/包中，并由`main`明确启动。Python模块顶层代码在导入时就会执行，Java类加载虽也可能有静态初始化，但通常不会把普通方法调用当成类加载的一部分。

<details><summary>先预测：另一段代码 import demo 时，会看到演示的三行输出吗？</summary>

不会。导入会执行函数定义和导入语句，但`__name__`不是`"__main__"`，因此`main()`不运行。
</details>

### 4. 位置与关键字参数

位置参数按顺序绑定：`select(records, 5)`把5绑定到`minimum`。关键字参数按名称绑定：`select(records, minimum=5)`把策略写清楚，读代码时不必回忆第二个参数的含义。`minimum`有默认值4，所以`select(records)`仍可调用。关键字调用依赖参数名称，重命名参数会影响这些调用点；位置调用依赖顺序，调整顺序也可能改变含义。

Java对照：Java通常靠重载或builder表达可选参数；Python关键字实参提供按名称传值的能力，但不是静态类型检查。

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

1. 运行`demo.py`时先执行`from rules import ...`。`rules.py`建立函数对象，不运行筛选循环，所以此时没有输出。
2. 入口判断为真，`main()`开始；`records`绑定到含T1/T2的列表。
3. 调用`select(records, minimum=4)`，实参`records`绑定到形参`tickets`，关键字值4绑定到`minimum`。初始`result=[]`。
4. 第一轮读取T1的优先级5，满足`5 >= 4`，追加ID；第二轮读取T2的优先级2，不追加。函数返回`['T1']`，`print`负责显示。
5. `add_tag('urgent')`收到默认`None`，创建新列表并追加urgent。下一次调用又从`None`开始，建立另一列表后追加review，因此第二行不会包含urgent。

可在`rules.py`里把阈值改为5，预测筛选列表再运行；也可临时让函数只print不return，观察显示仍在但调用结果变成`None`。这些变化分别检验参数绑定和返回值契约。

## Java 对照

Python函数常写在模块中，Java则常放在类或接口实现中；Python不支持按参数签名同时定义多个同名函数，后一次`def`会覆盖前一次。Python默认参数减少重载数量，但可变默认值共享这一点需要特别处理。Python代码块由缩进确定；本课类型检查则通过实际比较和分支完成，而不是靠注解。

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
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 03`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
