# 阶段 04：文件、JSON与异常边界

## 使用场景

工单需要保存为JSON，重启后读取。损坏文件不能被悄悄当成空工单，否则会把数据事故隐藏起来。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 区分路径定位、文本解码、JSON解析与业务字段校验四个步骤。
- 用相同编码写入和读取中文数据，说明with何时关闭文件。
- 区分合法空列表、文件丢失、文本损坏与字段错误。
- 独立校验工单ID，保留失败原因，不用空结果掩盖错误。

## 前置知识与阅读顺序

先完成阶段 03 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 路径与编码

程序要打开文件，先要把“文件叫什么”与“从哪里找”分开。`Path("tickets.json")`是相对路径，解释基准是当前工作目录（PowerShell中可用`Get-Location`查看），不是Python文件所在目录。临时演示用`Path(temporary) / "tickets.json"`，把文件放在`TemporaryDirectory`实际创建的目录中，退出`with`后目录会清除。

文本文件必须明确编码。`write_text(..., encoding="utf-8")`把Python字符串编码成UTF-8字节；`open("r", encoding="utf-8")`再按同一规则解码。漏写编码会依赖机器默认设置，中文文件可能在另一台Windows机器上读错。UTF-8不能修复本身已损坏或实际采用其他编码的文件，遇到`UnicodeDecodeError`应确认数据来源。

Java对照：`Path`与`Files`类似，路径本身只是位置描述；真正读写由open/read/write完成。二者都应避免把工作目录误当成源码目录。

<details><summary>先预测：从项目根运行demo时，Path("tickets.json")指向哪个目录？</summary>

它相对于当前工作目录，也就是项目根目录。演示没有使用裸相对路径，而是先用临时目录构造完整路径，因此不会把临时数据误写进仓库。
</details>

### 2. JSON与校验

先暂时不碰磁盘，只观察一段文本怎样变成Python值：

```python
import json

# 外层单引号是Python字符串界限，内层双引号属于JSON文本。
text = '{"id": 7}'
record = json.loads(text)
print(record["id"])
print(isinstance(record["id"], str))
```

先输出7，再输出False。`import json`把标准库模块提供的功能引入当前文件，`json.loads(text)`把字符串作为输入进行解析，返回一个字典。`isinstance(value, str)`询问value是不是字符串对象；本例解析出的7是整数，因此为False。没有异常不等于数据可用于当前业务，它只表示当前这一步做完了。


JSON只规定文本的结构。`json.dumps`把Python对象编码成JSON字符串，`json.loads`解析已有字符串，`json.dump/load`则对文件句柄工作。解析成功只说明文本语法合法：`{"id": 7}`完全是合法JSON，但本业务要求工单ID为字符串，仍须额外检查。

本课`load_tickets`先取到Python值，再检查顶层必须是list、每项必须是dict、`id`必须是str。空字符串ID在演示中没有被拒绝（独立练习将要求非空ID）；不要把练习契约混成演示已经实现的规则。`ensure_ascii=False`只影响序列化后中文字面的写法，不改变数据含义。

Java对照：Jackson能把JSON转成对象，但目标字段约束和业务不变量仍需要校验。Python的dict结构灵活，读取外部数据时更要显式确认类型和必填字段。

<details><summary>先预测：{"id": 7}会在哪一步失败？</summary>

JSON解析不会失败；它解析成字典后，`isinstance(ticket.get("id"), str)`为假，业务校验抛`ValueError`。损坏文本则在`json.load`阶段先抛`JSONDecodeError`。错误发生层不同，恢复方式也不同。
</details>

### 3. 异常与上下文管理

下面用一个完整的小例子观察执行跳转。这里捕获错误是为了演示，不是把错误数据当成空工单：

```python
import json

try:
    # 这个字符串少了完整结构，解析会失败。
    record = json.loads("{")
    print("只有解析成功才会到这里")
except json.JSONDecodeError:
    print("文本损坏，需要修复后再读")
```

`try`标出我们预期可能失败的操作；`except`后面写要处理的异常类型。执行解析时抛出指定异常，控制流跳过try里剩余语句，进入except，所以这里只输出“文本损坏，需要修复后再读”。`raise ValueError(...)`则是程序主动报告输入不符合业务要求；它不是打印一条警告后继续正常路径。


发生异常时，当前正常路径会被跳过，Python向外寻找匹配的`except`。`json.load`的JSON语法错误是`JSONDecodeError`；文件不存在是`FileNotFoundError`；结构合法但字段不符合本业务时由我们主动`raise ValueError`。把三者全部捕获并返回空列表，会把“没有工单”“路径错了”和“数据损坏”伪装成同一件事。

`with path.open(...) as handle:`进入时获取文件句柄，退出时自动关闭；正常返回、字段校验失败或解析失败都会经过退出逻辑。调用者只处理它能恢复的异常，不能用`except Exception: pass`隐藏错误。日志补充示例中，`finally`用于无条件清理，`logger.warning`用于开发者诊断，而业务函数仍向调用者抛出明确错误。

Java对照：with的资源生命周期与try-with-resources相近；Python不要求函数声明`throws`，所以接口文档和测试要说明可能抛出的异常。

<details><summary>先预测：损坏的JSON会进入字段循环吗？文件句柄会关闭吗？</summary>

不会进入字段循环，`json.load`先抛出`JSONDecodeError`；离开`with`时句柄仍会关闭。捕获该异常只用于展示“保留损坏状态”，并没有把文件改写为空列表。
</details>

### 4. 日志

`logging_demo.py`在`main`入口配置命名logger，随后以`WARNING`等级输出文件标识和错误类别。日志面向维护者；返回值或异常面向调用者。打印整个工单或异常正文可能把个人信息、密钥带入日志系统。本例只记录固定的`file_id`与`json_corrupted`，既能定位类型，也不暴露正文。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/04-files-errors/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
读取：[{'id': 'T1', 'title': '无法登录'}]
读取失败：JSON损坏，保留错误并等待修复
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""临时目录读写，不在项目中留下测试数据。"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

def load_tickets(path):
    # with保证读取成功或失败后文件句柄均关闭。
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("工单文件必须是列表")
    for ticket in data:
        if not isinstance(ticket, dict) or not isinstance(ticket.get("id"), str):
            raise ValueError("每个工单必须包含字符串id")
    return data

def main():
    # 临时目录退出后自动清理，适合可重复演示。
    with TemporaryDirectory() as temporary:
        path = Path(temporary) / "tickets.json"
        path.write_text(json.dumps([{"id": "T1", "title": "无法登录"}], ensure_ascii=False), encoding="utf-8")
        print(f"读取：{load_tickets(path)}")
        path.write_text("{broken", encoding="utf-8")
        try:
            load_tickets(path)
        except json.JSONDecodeError:
            # 保留“损坏”的错误语义，不伪造成没有工单。
            print("读取失败：JSON损坏，保留错误并等待修复")

if __name__ == "__main__":
    main()
```

## 代码执行过程与逐段解释

1. 直接运行时`main`创建临时目录；路径`temporary/tickets.json`只在本次演示期间存在。
2. `json.dumps(..., ensure_ascii=False)`产生包含中文的JSON文本，`write_text`按UTF-8写入。文件内容此时是合法的工单列表。
3. `load_tickets`打开文件并解析。顶层是list，第一项是dict，`id`是字符串，所以返回原列表并显示T1。
4. 演示用`write_text("{broken")`覆盖同一个文件。第二次进入`json.load`时，语法分析失败，后续的`isinstance`循环不会执行；`JSONDecodeError`被窄范围捕获并转换为一条清楚的演示提示。
5. 提示说“等待修复”，而不是返回空列表。离开临时目录的`with`后，目录及其中的损坏样本自动清除。

反例：若捕获所有异常并`return []`，调用者无法知道自己得到的是“确实没有工单”还是“读取失败”。练习要求重复ID拒绝，还要分别验证解析错误与业务校验错误。

## Java 对照

Java的try-with-resources与Python`with`都能自动关闭文件；Jackson映射成功也不代表工单字段符合业务规则。Java常在签名或文档中声明异常，Python通常通过函数契约和测试表达。Python的动态字典尤其需要在解析后检查类型和必填字段。

## 易错点与排查

- UnicodeDecodeError：文件实际编码不匹配，先确认来源，不要errors="ignore"丢字。
- JSON使用单引号：JSON字符串必须双引号；Python字典写法不是JSON文本。
- 路径找不到：打印工作目录并检查文件位置，不要猜测路径。
- 宽泛捕获：区分不存在、损坏与缺失字段，调用者才知道是否重试。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data为JSON文本，必须解析为工单列表；每条需要非空字符串id；重复id拒绝；返回工单数量。分别验证损坏文本、重复id和空列表。不得读取或覆盖真实工单文件。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/04-files-errors/exercises/practice.py
python lessons/04-files-errors/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

## 企业工程延伸

直接覆盖文件可能在崩溃时截断数据。后续持久化阶段使用同目录临时文件、原子替换或数据库事务；读写路径也要限制在授权工作空间。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/json.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

## 日志补充演示

从根目录执行 `python lessons/04-files-errors/examples/logging_demo.py`，实际输出：

```text
WARNING ticket_import event=load_failed file_id=teaching-fixture error=json_corrupted
```

[日志源码](examples/logging_demo.py)在入口配置命名logger；不在模块导入时改全局配置。
`StreamHandler`决定日志去向，`Formatter`决定显示格式，`setLevel`决定最低记录级别。
DEBUG用于细节诊断，INFO用于正常事件，WARNING用于可处理异常，ERROR用于失败。
`logger.warning`记录开发者事件；它不会代替给业务调用者返回失败。
这里不记录整个工单或异常正文，避免业务资料进入无控制的日志。
`finally`无论成功还是异常都执行，用于清理；`with`通常能表达同样的资源生命周期。
`raise ValueError(...)`主动拒绝无效数据，`except ... as error`把异常对象绑定到名称。
[Python日志官方资料](https://docs.python.org/zh-cn/3.12/library/logging.html)。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 04`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
