# 阶段 28：本地MCP接入

## 使用场景

把工单查询封装为可发现的工具，并区分工具、资源和提示模板。

主线项目是企业知识与工单协作助手。本阶段只增加一个可解释的能力边界，先验证机制，再讨论规模化。
运行演示不需要模型密钥，也不会请求真实业务系统。

## 学习目标

- 能区分工具调用、只读资源和提示模板，并按请求方法进入对应分支。
- 能从请求中读取工具名与参数，区分未知方法、未知工具和非法参数。
- 能说明本地dispatch不是MCP传输实现，并保留真实SDK集成边界。

## 前置知识

真正先修是阶段11的工具名称、参数和错误契约；本课只模拟MCP dispatch方法，不要求先安装SDK。

## 概念：先发现契约，再按契约调用

本地dispatch演示只有两类请求：`tools/list`返回可用工具描述；`tools/call`根据`params.name`找到工具，再验证参数。发现阶段说明`get_ticket`需要`ticket_id`，调用阶段仍要检查该值确实是非空字符串。工具名和参数不能直接变成任意Python函数名或属性访问。

下面摘录或简化本课示例的关键步骤，需结合[完整源码](examples/demo.py)中的定义与上下文阅读；运行时使用下方演示命令。

```python
if method == "tools/list":
    return {"tools": TOOLS}
if params.get("name") != "get_ticket":
    raise ValueError("未知工具")
```

预测用`ticket_id="T1"`调用：通过名称与字段检查，结果`found=True`并带回副本工单；缺少ticket_id会抛ValueError；未知工具也会在查询工单字典之前拒绝。副本避免调用者修改返回内容时反向改变示例数据库。

<details><summary>展开推导：tools/list返回get_ticket后，调用者传入name=delete_ticket，是否能执行删除？</summary>

不能。`dispatch`只允许精确名称`get_ticket`，否则抛ValueError；清单返回的描述不会自动注册任意操作。演示也没有真实JSON-RPC envelope、MCP初始化或传输，因此只证明本地方法分发边界。
</details>

Java对照：可把工具表对应到明确的接口注册表，参数验证对应DTO校验；不要通过反射让外部字符串调用任意方法。真实MCP还需遵循协议握手、错误结构与生命周期。

## 演示文件与执行命令

默认工作目录是项目根目录 `C:\Users\Mason\Desktop\agent-study`。
如已创建虚拟环境，可以把python替换成 `.\.venv\Scripts\python.exe`，无需激活或修改执行策略。

```powershell
python lessons/28-mcp-local/examples/demo.py
python lessons/28-mcp-local/solutions/solution.py
python -m unittest discover -s lessons/28-mcp-local/tests -v
```

第一条运行演示；第二条仅在完成练习后阅读与运行；第三条执行本阶段行为检查。
`-m`表示让解释器把模块当入口，`discover`搜寻test_开头文件，`-s`指定测试目录，`-v`显示每个测试名字。
测试正常时结尾是 `OK`。故意运行未完成的练习函数出现NotImplementedError，代表你还需要实现，不代表环境坏了。

### 默认演示预期输出

```text
{'tools': {'get_ticket': {'description': '查询工单', 'required': ['ticket_id']}}}
{'found': True, 'ticket': {'status': 'open', 'title': '登录失败'}}
```

### 预期输出如何阅读

第一行tools/list返回get_ticket的描述与必需ticket_id参数；第二行tools/call执行本地只读夹具，返回T1的open状态和标题。输出不是MCP JSON-RPC传输证明，真实初始化/生命周期在集成入口验收。

## 执行过程与状态变化

1. tools/list发现工具契约。
2. tools/call选择受控工具。
3. 先验证字符串参数，再查询工单。
4. 返回found区分不存在与调用失败。

正常请求先列出get_ticket元数据，再以ticket_id=T1调用并取得open状态。这里的TOOLS字典只是允许操作列表，不能代替调用者身份或服务端对象权限。

## 对照源码的逐行解释

按examples/demo.py中的顺序阅读，下列关键表达式决定正常与失败路径。

| 表达式或位置 | 为什么这样写及状态变化 |
|---|---|
| `request.get("method")` | 演示方法名对应发现或调用，缺失方法明确失败；没有实现initialize，故不是完整MCP。 |
| `params与arguments` | 分开工具选择与业务参数；只允许受控get_ticket，不按任意字符串动态执行函数。 |
| `isinstance(identity, str)` | 数字、None或空字符串都不是有效工单标识，必须先拒绝再查询。 |
| `found与ticket` | 工单不存在是业务结果，协议参数错误是调用失败，不能混成同一个空字典。 |
| `真实SDK结构化结果` | v2中裸dict返回注解可能只有文本内容；集成使用BaseModel生成输出Schema并断言structured_content。 |
| `资源与提示` | policy://current读取资料，summarize_ticket生成提示；后者不会自动查询数据库或保证回答正确。 |
| `REST对照` | REST按HTTP路由定义业务接口，MCP额外定义能力发现、类型化调用与宿主交互；服务仍可在内部调用REST系统。 |

## Java Web对照

MCP不是把Spring Bean名字直接暴露给客户端；协议还规定发现、调用和传输消息。本地字典只演示方法分派与参数验证。

## 易错点与排错顺序

1. 文件路径错误：确认终端在项目根目录，先运行演示而不是练习骨架。
2. 把空结果当成功：查返回状态与来源，不能编造缺失字段或证据。
3. 在失败后继续修改：先验证再变更，给失败输入补行为测试。
4. 共享可变对象：调用前后打印输入，确认是否被无意修改。
5. 把模拟效果当生产质量：检查本页边界说明与真实接入目录。
6. 只看最终回答：保留查询、状态或执行轨迹，定位失败发生在哪一步。

## 独立练习

为工具调用添加请求级错误结果：未知方法、未知工具与非法参数应区分错误码；不能把异常堆栈作为正文返回。用真实SDK客户端完成发现、资源读取和提示获取。

打开 [练习要求](exercises/README.md)，在 [practice.py](exercises/practice.py) 实现。
骨架有意留下待实现函数，示例和参考答案不能替代你自己的思考与测试。
自动校验保存协议子集的错误分类；真实SDK客户端发现、资源读取与提示获取仍需独立集成验收。

## 能力验收

- 能不看代码解释至少三个概念，并各举一个企业助手场景。
- 能预测演示执行前后的关键字段，再通过运行核对。
- 能独立修改一项业务规则并解释对结果的影响。
- 能让一个失败输入按预期被拒绝，且不产生越权或错误证据。
- 能说明本课测试证明了什么、没有证明什么。

材料制作、代码验证、学员掌握是三种状态；本课提供材料与验证方法，学员能力仍待验收。

## 工程延伸与边界

默认dispatch不是完整MCP也不是JSON-RPC实现。integrations使用官方Python SDK启动真实stdio子进程与会话。

从本课迁移到企业项目时，先写输入输出契约与独立评估案例，再决定存储、模型和框架。
保留可追溯来源和任务/身份信息，让问题能定位到具体数据与步骤。
添加性能优化前先检查正确性，尤其是失败时是否仍保护权限、预算和有效状态。
单元测试覆盖本地规则；真实网络、持久化、并发与供应商行为需要额外集成验证。

## 官方资料与复习

- [本课官方参考](https://github.com/modelcontextprotocol/python-sdk)：查API或协议边界，不要求一次读完。
- [Python 3.12教程](https://docs.python.org/zh-cn/3.12/tutorial/)：复习循环、函数、异常和模块。
- [本课知识卡](knowledge.md)：按定义、案例、误区整理。
- [验证记录](verification.md)：仅记录实际执行范围，不能据此声称生产部署通过。

## 真实集成入口

打开[集成说明](integrations/README.md)，按独立环境安装和验证；默认运行无需安装这些依赖。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 28`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
