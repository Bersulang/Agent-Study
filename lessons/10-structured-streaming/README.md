# 阶段 10：结构化输出、SSE与取消

## 使用场景

助手流式生成工单草稿，前端需要逐步显示，但业务系统只能接收完整且校验通过的对象。半段JSON和断流不能触发创建工单。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能区分传输块、SSE行、SSE事件和JSON对象四种边界。
- 能解释UTF-8增量解码、空行提交和[DONE]应用完成标记如何共同决定是否有完整草稿。
- 能校验草稿字段，并确保断流、无结束标记或调用者取消时不提交半成品。

## 前置知识与阅读顺序

先完成阶段 09 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. JSON Schema与运行时校验

要把模型草稿交给业务系统，先把对象形状写清楚。本课只接受两个键：`title`和`priority`；前者必须是去掉首尾空格后仍非空的字符串，后者必须是严格整数1—5。示例Schema用`additionalProperties: false`禁止多余字段，但运行时仍需逐项校验，因为服务可能收到绕过模型Schema的输入。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
if not isinstance(value, dict) or set(value) != {"title", "priority"}:
    raise ValueError("字段必须恰好为title和priority")
if not isinstance(value["title"], str) or not value["title"].strip():
    raise ValueError("title必须非空")
```

即使JSON解析成功，`{"title":"登录失败","priority":true}`也不能通过严格priority规则；Python里bool是int子类。

Java对照：Jackson能反序列化DTO，但字段验证仍应由validator或业务代码完成；Schema不能替代服务端校验。

### 2. 网络块与SSE事件

`read()`得到的是任意长度字节块，而不是一行或一个JSON。服务器可以把中文“登”拆在两个字节块中，或把一条`data:`行切成多个块。`codecs.getincrementaldecoder("utf-8")()`记住尚未凑完整的字节；文本`buffer`再保存没有结束换行的半行。

```python
decoder = codecs.getincrementaldecoder("utf-8")()
buffer = ""
for chunk in chunks:
    buffer += decoder.decode(chunk)
```

只有找到完整行结束符后才处理该行；CRLF算一个换行，块末尾单独的CR要等下一块判断。SSE事件在空行边界提交。

### 3. data行与完成标记

空行把本次积累的多条`data:`行作为一个事件产出，行与行之间以换行连接。冒号开头的注释行是心跳，不进入业务数据；普通SSE规范并没有通用的`[DONE]`字段，这是本课Chat风格应用约定。EOF只意味着传输结束，不会自动补出缺失空行或完成标记。

示例wire把JSON刻意拆成两个SSE事件片段，再发`[DONE]`。`collect_draft`去掉SSE外层后拼接文本为完整JSON；生产Chat流通常还包在choices/delta JSON envelope中，需要先解envelope再累积content。

<details><summary>先预测：有空行但无[DONE]，与data行后立即EOF（两者都无）分别会怎样？</summary>

有空行时，parser会yield一个不完整事件，但`collect_draft`因没有[DONE]而抛`ValueError`，不解析或返回草稿。若空行和[DONE]都没有，SSE事件根本不会yield；循环结束后仍因缺少[DONE]抛`ValueError`。两种输入都不会提交半成品。
</details>

### 4. 取消与提交边界

`collect_draft`在本地`parts`里积累文本，只在读取到`[DONE]`、未被取消、成功拼成JSON并通过`validate_draft`之后才返回对象。取消检查在每个事件前及循环后执行；若取消，抛专用`StreamCancelled`，调用者应清理展示状态。UI可以显示“正在生成”预览，但预览不能当业务草稿提交。

此机制只管流接收，不执行工单写入；模型返回合法草稿也必须经过后续权限、人工审批和写工具。

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

1. `wire.encode()`把包含中文的文本编码成字节，切片每3字节组成一块。块边界可能正好落在中文字符内部。
2. 增量decoder逐块补齐UTF-8字符；`buffer`保留尚未见到行结束符的文本。parser遇到空行时，才把积累的data行以换行连接并yield事件。
3. `collect_draft`收到第一个JSON片段后只将其放入`parts`，还不是可提交对象；第二段事件提供剩余字段文本。
4. 收到`[DONE]`后设置`done=True`并结束读取；若调用者取消，则在此之前抛`StreamCancelled`。
5. 两段文本拼接成JSON后`json.loads`生成dict，再验证精确字段、非空title和1—5整数priority，最终才返回草稿。

断流反例：仅有`data: {"title":`并不构成完整事件/完整生成；即使前端已显示部分字符，没有[DONE]也不能提交。

## Java 对照

Java `InputStreamReader`与`BufferedReader`同样需要区分字节、字符和行；一次`read(byte[])`不是SSE事件边界。Python parser用生成器逐个yield完整事件，消费者再拼接应用层内容。无论语言为何，完整度和业务Schema都要显式确认。

## 易错点与排查

- 每个chunk解析JSON：块可能只是一个中文字符的一部分。
- 看到}就提交：括号可能在字符串中，必须依据协议完成事件。
- bool通过整数校验：Python bool继承int，严格Schema integer需特殊处理。
- 断流自动修复：最多有限重试/修正，不能给半成品添加字段后执行工具。

排查顺序：先查看原始字节块是否能完整UTF-8解码，再检查换行和空行事件边界；随后确认data累计、[DONE]完成标记和取消状态，最后检查JSON结构与业务字段。
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

1. 将含中文字节流切成任意小块，仍能解析相同SSE事件；说明传输块不是事件边界。
2. 校验title、priority及可选description；未知字段、空白标题和bool优先级均拒绝。
3. 缺少[DONE]、调用者取消或超过累计字节限制时，证明没有草稿返回。
4. 说明当前parser未实现重连、命名事件和供应商envelope适配。
5. 自动校验保存本地案例结果；真实EventSource行为需独立集成验收。

## 企业工程延伸

本课实现SSE数据字段与事件边界，未实现id重连、retry和命名事件分发；不是完整EventSource客户端。生产要处理连接超时、断连、流量上限与供应商事件JSON envelope。

本课SSE parser识别字段和事件边界，但没有实现id重连、retry、命名事件和完整EventSource客户端。供应商JSON envelope应单独适配；草稿对象与正式写入仍由后续权限、审批和工具阶段控制。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 10`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
