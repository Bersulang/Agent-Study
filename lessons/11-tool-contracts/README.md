# 阶段 11：工具契约与参数校验

## 使用场景

模型提出“查询T1工单”只是请求。程序必须确认工具存在、参数合法，再调用业务函数，结果由统一信封返回，不能让模型执行任意函数。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 10 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 工具描述与粒度

工具是被程序显式暴露的有限能力；描述告诉模型何时调用，参数与结果告诉程序如何校验。

用途与例子：ticket_lookup只查询单个工单，比一个可执行任意SQL或命令的万能工具更可控。

### 2. 参数Schema与业务校验

Schema约束输入形状；运行时校验是实际执行门禁，权限还需可信身份核查。

用途与例子：id必须非空字符串且没有额外字段；模型给出id并不证明有权读取它。

### 3. 结果信封与错误契约

统一结果结构包含ok、data、error；错误有稳定code和retryable。

用途与例子：not_found不应重试，temporary_unavailable可在预算内重试。

### 4. 注册表与分发

注册表把公开名字映射到已知函数，分发只访问白名单。

用途与例子：用TOOLS.get(name)，不使用eval、不按模型名称动态import。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/11-tool-contracts/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
{'ok': True, 'data': {'id': 'T1', 'status': 'open'}, 'error': None}
{'ok': False, 'data': None, 'error': {'code': 'invalid_arguments', 'message': 'id必须非空字符串', 'retryable': False}}
{'ok': False, 'data': None, 'error': {'code': 'unknown_tool', 'message': '未注册工具', 'retryable': False}}
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""只读工具契约；演示不包含身份系统，不能当完整权限实现。"""
TICKETS = {"T1": {"id": "T1", "status": "open"}}

TOOL_SPEC = {
    "name": "ticket_lookup",
    "description": "按工单id查询状态，不创建或修改工单",
    "parameters": {"type": "object", "properties": {"id": {"type": "string"}},
                   "required": ["id"], "additionalProperties": False},
}

def failure(code, message):
    return {"ok": False, "data": None,
            "error": {"code": code, "message": message, "retryable": False}}

def ticket_lookup(arguments):
    # 模型输出是不受信任输入，先校验再接触数据。
    if not isinstance(arguments, dict) or set(arguments) != {"id"}:
        return failure("invalid_arguments", "只接受id字段")
    identity = arguments["id"]
    if not isinstance(identity, str) or not identity.strip():
        return failure("invalid_arguments", "id必须非空字符串")
    if identity not in TICKETS:
        return failure("not_found", "工单不存在")
    # 返回副本，避免调用者通过结果改写数据源。
    return {"ok": True, "data": TICKETS[identity].copy(), "error": None}

TOOLS = {"ticket_lookup": ticket_lookup}

def dispatch(name, arguments):
    if not isinstance(name, str):
        return failure("unknown_tool", "工具名必须字符串")
    tool = TOOLS.get(name)
    if tool is None:
        return failure("unknown_tool", "未注册工具")
    return tool(arguments)

if __name__ == "__main__":
    print(dispatch("ticket_lookup", {"id": "T1"}))
    print(dispatch("ticket_lookup", {"id": 1}))
    print(dispatch("exec", {"command": "任意命令"}))
```

## 代码执行过程与逐段解释

1. TOOL_SPEC只是声明，没有自动执行Python校验；真实供应商需转换成其工具格式。
2. dispatch按已注册字符串名称查表，unknown_tool返回错误。
3. ticket_lookup检查对象、精确字段集合、字符串与空白，再查询。
4. 未找到与无效参数分别使用not_found、invalid_arguments。
5. 成功信封里data为副本，error为None，调用者按ok分支处理。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

相当于Java REST DTO校验与Service方法白名单；描述类似OpenAPI但不是授权。Python函数可作为字典值直接传递，调用tool(arguments)不需要反射。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 只写Schema不校验：本地函数收到非法数据仍会执行。
- 模型要求新工具就动态导入：注册表应由开发者控制。
- 错误只是一段文本：上层难以判断重试，使用稳定code。
- 工具返回原对象：调用者可能改写共享状态。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data含name与args，新增ticket_search按status查询，status只允许open或closed。返回稳定信封，未知工具/非法参数有不同code；不得执行eval或任意属性访问。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/11-tool-contracts/exercises/practice.py
python lessons/11-tool-contracts/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

查询与写入工具分开，写入需要审批与幂等。输出限制字段和大小，避免大量敏感数据进入模型上下文；真实身份由服务器注入而不是模型参数指定。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://json-schema.org/understanding-json-schema/reference/object)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/11-tool-contracts/tests -v`。

## 契约和身份的两个边界

模型生成的name/args均不可信；查表限制能力，字段校验限制调用形状。
调用者身份不能放在可由模型任意填写的args中，真实服务应从已认证上下文传入。
工具description帮助选择，但不能绕过执行器校验。
`set(arguments) != {"id"}`要求字段集合恰好相同；{}是字典，{"id"}是只有一个元素的集合。
