# 阶段 11：工具契约与参数校验

## 使用场景

模型提出“查询T1工单”只是请求。程序必须确认工具存在、参数合法，再调用业务函数，结果由统一信封返回，不能让模型执行任意函数。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能将模型给出的工具名映射到开发者维护的白名单函数，而不动态执行名字。
- 能在任何数据访问前校验参数类型、必填字段、额外字段与业务值。
- 能返回稳定结果信封，并区分未知工具、非法参数、未找到和成功。
- 能解释工具描述、Schema、运行时校验与真实身份授权各自解决的问题。

## 前置知识与阅读顺序

先完成阶段 10 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 工具描述与粒度

工具是程序显式提供的有限能力。`ticket_lookup`只允许按ID查询状态；它不执行SQL、不创建工单，也不接收命令。描述让模型知道这个工具适合什么请求，但它不是权限边界，实际调用仍由dispatch和后端授权控制。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
TOOLS = {"ticket_lookup": ticket_lookup}
tool = TOOLS.get(name)
if tool is None:
    return failure("unknown_tool", "未注册工具")
```

白名单将模型可以请求的名字限制为开发者注册的函数。不存在的`exec`只得到unknown_tool，不会经过eval或任意import。

Java对照：可类比显式注册的Service方法或REST路由；工具schema像OpenAPI契约，但描述本身不授权调用者。

### 2. 参数Schema与业务校验

`TOOL_SPEC`要求参数为对象、恰有id字段且不接受额外属性；但这份声明只是元数据。`ticket_lookup`还要在运行时检查`arguments`真的是dict、键集合精确相等、id是非空字符串，然后才查`TICKETS`。否则`{"id":1}`可能被带到数据层，`{"id":"T1","admin":true}`可能被误解为模型有权扩展操作。

真实用户身份不能来自模型可控的args。业务服务应从已认证会话取得身份，再对目标工单做对象级授权；本例只有固定数据，没有身份系统。

<details><summary>先预测：arguments是{"id":"T1","extra":true}，Schema有additionalProperties=false，但Python函数不执行Schema校验时会怎样？</summary>

只有实际运行时的`set(arguments) != {"id"}`检查能保证函数拒绝它；Schema声明并不会自动拦截本地Python调用。
</details>

### 3. 结果信封与错误契约

`failure`把失败统一为`{"ok":False,"data":None,"error":{"code":...}}`；成功返回`ok=True`、数据副本和`error=None`。稳定错误码让上层能决定如何处理：`invalid_arguments`要修输入，`unknown_tool`要检查版本/注册表，`not_found`通常不是瞬态故障。当前demo把所有错误的retryable设为False，没有演示瞬态网络工具。

### 4. 注册表与分发

注册表`TOOLS`把外部公开名称映射到可调用对象。`dispatch`先确认name是字符串，再查表；找到函数后才用`tool(arguments)`调用。不能用`eval(name)`，也不能依模型给出的名字动态import任意模块。

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

第一个调用`dispatch("ticket_lookup", {"id":"T1"})`：name是字符串且在TOOLS中，arguments正好有id，id非空，数据表命中T1，于是返回成功信封，data是字典副本。第二个调用id是整数，在查表前返回invalid_arguments。第三个调用exec不在TOOLS中，返回unknown_tool，任意command字段不会被执行。

反例：即使name与参数均合法，若服务没有核验当前用户是否能查看T1，仍可能越权。本地规则只验工具边界，不是身份授权。

## Java 对照

Java REST DTO校验对应参数形状检查，Service白名单对应TOOLS注册表。Python函数可直接作为字典值调用，无需反射；Java通常会在编译期检查一部分类型，但服务仍需验证外部JSON与对象级权限。

## 易错点与排查

- 只写Schema不校验：本地函数收到非法数据仍会执行。
- 模型要求新工具就动态导入：注册表应由开发者控制。
- 错误只是一段文本：上层难以判断重试，使用稳定code。
- 工具返回原对象：调用者可能改写共享状态。

排查顺序：先判断失败在name类型/注册表还是参数校验；然后检查信封code、目标是否存在以及data是否为副本；若是生产权限问题，另追身份上下文与对象授权，不能只调Schema。
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

1. 新增`ticket_search`并按status检索工单，只允许open和closed。
2. 对成功、未知工具、额外字段和非法status分别返回稳定且不同的错误信封。
3. 证明工具参数校验发生在数据访问前，执行器不调用eval或任意属性访问。
4. 说明身份必须来自可信认证上下文，工具描述和模型参数都不能授予权限。
5. 自动校验保存离线分发结果；真实身份与审计仍按集成标准验收。

## 企业工程延伸

查询与写入工具分开，写入需要审批与幂等。输出限制字段和大小，避免大量敏感数据进入模型上下文；真实身份由服务器注入而不是模型参数指定。

本课只实现静态只读ticket_lookup，没有身份校验、审计、远端I/O或写工具。练习增加按status筛选的只读能力；后续写操作仍需要审批和幂等边界。

## 官方资料与教学边界

- [官方参考](https://json-schema.org/understanding-json-schema/reference/object)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/11-tool-contracts/tests -v`。

## 契约和身份的两个边界

模型生成的name/args均不可信；查表限制能力，字段校验限制调用形状。
调用者身份不能放在可由模型任意填写的args中，真实服务应从已认证上下文传入。
工具description帮助选择，但不能绕过执行器校验。
`set(arguments) != {"id"}`要求字段集合恰好相同；{}是字典，{"id"}是只有一个元素的集合。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 11`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
