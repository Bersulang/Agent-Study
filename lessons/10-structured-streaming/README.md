# 阶段 10：结构化输出、SSE与取消

## 使用场景

助手流式生成工单草稿，前端需要逐步显示，但业务系统只能接收完整且校验通过的对象。半段JSON和断流不能触发创建工单。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 09 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. JSON Schema与运行时校验

Schema描述对象字段、类型与约束；结构化输出能力支持范围依供应商而变。

用途与例子：title必填非空，priority整数1—5，additionalProperties=false拒绝额外字段；仍需业务验证。

### 2. 网络块与SSE事件

网络read返回字节块，边界任意；SSE按UTF-8文本行解析，用空行提交事件。

用途与例子：一个事件可横跨多个字节块；中文可在多字节中间切开，必须增量解码。

### 3. data行与完成标记

多个data行以换行连接；注释心跳不产生业务数据；EOF不自动提交未终止事件。

用途与例子：[DONE]是本课Chat风格应用标记，不是SSE规范通用字段，Responses事件另有结构。

### 4. 取消与提交边界

取消使生成停止；只有完整完成并校验后才能发布草稿。

用途与例子：先展示临时文本，最终返回对象；取消或缺少完成标记丢弃未提交草稿。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/10-structured-streaming/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
已校验草稿：{'title': '登录失败', 'priority': 4}
拒绝：流未完整结束，草稿未提交
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""真实SSE文本边界解析；本地字节流是教学夹具。"""
import codecs
import json

class StreamCancelled(Exception):
    """调用者取消，不允许提交半成品。"""

def sse_events(chunks):
    decoder = codecs.getincrementaldecoder("utf-8")()
    buffer = ""
    data = []
    first = True
    for chunk in chunks:
        text = decoder.decode(chunk)
        if first and text:
            text = text.removeprefix("\ufeff")
            first = False
        buffer += text
        # 同时识别LF、CRLF、CR；末尾CR需等下一块确认是否CRLF。
        while True:
            positions = [i for i, char in enumerate(buffer) if char in "\r\n"]
            if not positions:
                break
            end = positions[0]
            if buffer[end] == "\r" and end == len(buffer) - 1:
                break
            width = 2 if buffer[end:end + 2] == "\r\n" else 1
            line, buffer = buffer[:end], buffer[end + width:]
            if line == "":
                if data:
                    yield "\n".join(data)
                    data = []
            elif not line.startswith(":"):
                field, separator, value = line.partition(":")
                if value.startswith(" "):
                    value = value[1:]
                if field == "data":
                    data.append(value if separator else "")
    # 检查残缺UTF-8；EOF不把未结束事件提交。
    decoder.decode(b"", final=True)
    if buffer == "\r" and data:
        # 一个尾部CR结束空行，此时确实有事件边界。
        yield "\n".join(data)

def validate_draft(value):
    if not isinstance(value, dict) or set(value) != {"title", "priority"}:
        raise ValueError("字段必须恰好为title和priority")
    if not isinstance(value["title"], str) or not value["title"].strip():
        raise ValueError("title必须非空")
    if type(value["priority"]) is not int or not 1 <= value["priority"] <= 5:
        raise ValueError("priority必须为1到5整数")
    return value

def collect_draft(chunks, cancelled=lambda: False):
    parts = []
    done = False
    for event in sse_events(chunks):
        if cancelled():
            raise StreamCancelled("已取消，草稿未提交")
        if event == "[DONE]":
            done = True
            break
        parts.append(event)
    if cancelled():
        raise StreamCancelled("已取消，草稿未提交")
    if not done:
        raise ValueError("流未完整结束，草稿未提交")
    return validate_draft(json.loads("".join(parts)))

if __name__ == "__main__":
    # 模拟应用直接在data中发文本；真实供应商常发JSON envelope，需要适配。
    wire = 'data: {"title":"登录失败",\n\ndata: "priority":4}\n\ndata: [DONE]\n\n'.encode()
    chunks = [wire[i:i + 3] for i in range(0, len(wire), 3)]
    print(f"已校验草稿：{collect_draft(chunks)}")
    try:
        collect_draft([b'data: {"title":\n\n'])
    except ValueError as error:
        print(f"拒绝：{error}")
```

## 代码执行过程与逐段解释

1. UTF-8增量解码器保留尚未完整的多字节字符；buffer保留跨块文本行。
2. 扫描CR与LF，CRLF视为一个换行；末尾CR等待后续块，注释行跳过。
3. 空行提交data列表；同一事件多行data用换行连接，不能逐read调用json.loads。
4. collect_draft拼接不同delta事件，等[DONE]；取消会抛出专门异常。
5. json.loads后validate_draft执行类型和字段校验；返回的只是草稿，写入另需审批。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

可类比Java InputStreamReader处理字节到字符，BufferedReader.readLine处理行；read(byte[])不能当消息边界。Python生成器以yield交付事件，消费者可以在完成后停止读取。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 每个chunk解析JSON：块可能只是一个中文字符的一部分。
- 看到}就提交：括号可能在字符串中，必须依据协议完成事件。
- bool通过整数校验：Python bool继承int，严格Schema integer需特殊处理。
- 断流自动修复：最多有限重试/修正，不能给半成品添加字段后执行工具。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：输入完整JSON字符串，校验title/priority，新增description可选且必须字符串，拒绝未知字段；不自动修复。另给流式收集增加最大累计字节上限，超过上限停止且不得返回草稿。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/10-structured-streaming/exercises/practice.py
python lessons/10-structured-streaming/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

本课实现SSE数据字段与事件边界，未实现id重连、retry和命名事件分发；不是完整EventSource客户端。生产要处理连接超时、断连、流量上限与供应商事件JSON envelope。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://html.spec.whatwg.org/multipage/server-sent-events.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

[JSON Schema对象约束](https://json-schema.org/understanding-json-schema/reference/object)。已于2026-10-06核查SSE官方规范；测试：`python -m unittest discover -s lessons/10-structured-streaming/tests -v`。

## Schema、修复与流事件再区分

[草稿Schema](examples/draft.schema.json)记录结构约束；JSON不支持注释，文件说明在本讲义。
`minLength: 1`允许空白字符串，本课运行时额外用strip拒绝只包含空格的标题。
`set(value)`得到字典键集合，精确相等拒绝额外字段；不是比较所有字段值。
`partition(":")`分割为字段名、分隔符、剩余内容，避免把data中后续冒号切碎。
`lambda: False`返回默认取消状态，调用者可传函数读取自己的取消令牌。
生产Chat流通常发送包含choices/delta的JSON，先从SSE解析事件，再解析供应商envelope，最后累计content。
字段修复必须有限次数且记录错误；本课故意拒绝非法对象，不把自动补全当可靠事实。
缺少结束标记属于未完成，本课不会自动重试生成。取消后既不提交草稿也不执行工具。
