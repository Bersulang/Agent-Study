# 阶段03知识整理：函数、作用域与模块

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 函数返回的是什么？

看[规则实现](examples/rules.py)里的`select`：循环把符合`priority >= minimum`的ID放进`result`，最后`return result`。输入T1优先级5、T2优先级2且阈值4时，结果为`['T1']`。如果改成只`print(result)`，控制台仍会显示列表，但调用表达式的值是`None`，所以“看到结果”并不等于“调用者拿到了结果”。

## 为什么默认参数不要放空列表？

Python在执行`def`时就创建默认对象；可变对象可能被后续调用共同引用。`add_tag(name, tags=None)`用`None`表示未提供，再在每次函数调用时创建列表。两次调用分别得到`['urgent']`与`['review']`。若写默认`tags=[]`并原地追加，第二次就可能变成`['urgent', 'review']`。显式传入列表时，本例还复制列表，避免改动调用者的数据。

## 导入时为什么不应运行整个程序？

`demo.py`先导入`rules.py`，然后由`if __name__ == "__main__"`决定是否调用`main()`。直接运行时入口条件成立；被其他模块导入时不成立。若把网络请求或文件写入放在模块顶层，测试只想导入函数也会触发这些副作用。脚本路径运行时的同目录查找机制也不等于任意目录都能导入同名文件。

## 位置参数还是关键字参数？

`select(records, 5)`靠顺序解释5；`select(records, minimum=5)`把含义写在调用处，更方便阅读和扩展可选策略。前者受参数顺序影响，后者受参数名影响。修改规则前要查清调用方依赖了哪种绑定方式。

## 执行与失败路径

解释器执行from rules import，从同目录rules.py导入函数；模块只定义函数，不打印。

运行路径是`demo -> 导入rules -> 入口判断 -> main -> select/add_tag -> print`。筛选过程中局部列表依次为`[]`、`['T1']`；阈值改为5时仍包含T1，改为6时变成空列表。两次标签调用的初值都是None，因此各自新建列表；若把函数改成修改共享默认列表，重复运行就会暴露状态污染。

## Java迁移

Java通常将规则放在类或静态方法中，Python函数可以直接位于模块。Java可按签名重载，Python同名`def`会覆盖先前绑定；Python默认实参可以代替一些重载，但可变默认值的生命周期更容易造成意外共享。

## 工程应用

服务端把I/O与纯规则分开后，可以直接向`select`传入测试工单，而不用先启动数据库或模型。模块适合承载可导入规则；只有程序入口负责打印、网络或命令行交互。

## 复习与验证

复习时先不运行：如果阈值从4变为6，T1/T2分别如何处理？如果连续调用`add_tag`两次，第二次看到第一次的标签吗？写下预测，再对照演示输出。随后完成[独立练习](exercises/README.md)，确认函数返回值、输入列表和连续调用状态；参考答案能运行不代表你已掌握。

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
