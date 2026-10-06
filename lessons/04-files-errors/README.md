# 阶段 04：文件、JSON与异常边界

## 使用场景

工单需要保存为JSON，重启后读取。损坏文件不能被悄悄当成空工单，否则会把数据事故隐藏起来。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 03 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 路径与编码

Path表示文件路径；相对路径根据当前工作目录解释；UTF-8规定字符与字节互换。

用途与例子：中文JSON明确encoding="utf-8"，不依赖Windows默认编码。

### 2. JSON与校验

JSON是数据交换格式，loads把文本解析成Python对象；语法正确不代表字段正确。

用途与例子：{"id":7}可解析，但工单id要求字符串时应拒绝。

### 3. 异常与上下文管理

异常将正常执行转向匹配的except；with在退出时释放资源。

用途与例子：FileNotFoundError与JSONDecodeError不同，不能一律返回空列表。

### 4. 日志

日志记录事件与定位信息；业务数据和密钥不应原样全部记录。

用途与例子：本课返回具体错误，生产日志可记录文件标识与错误类别。

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

1. 标准库模块导入后，main创建临时目录与Path对象。
2. dumps返回JSON字符串，ensure_ascii=False保留中文显示；write_text写UTF-8。
3. json.load读取并解析，之后逐条检查字段；isinstance检查实际对象类型。
4. 覆盖为损坏内容后第二次读取抛出JSONDecodeError，进入指定except。
5. 离开with清理临时目录；没有把损坏文件恢复为空列表。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

Java try-with-resources对应with；Jackson反序列化也要业务校验。Python异常无需throws声明，异常契约必须通过函数说明与测试明确。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

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
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

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
