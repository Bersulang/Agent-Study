# 阶段 29：远程MCP与故障边界

## 使用场景

远程工具服务断连或工具清单变化，客户端要更新发现结果并避免重试越权写入。

主线项目是企业知识与工单协作助手。本阶段只增加一个可解释的能力边界，先验证机制，再讨论规模化。
运行演示不需要模型密钥，也不会请求真实业务系统。

## 学习目标

- 能解释一次断连最多尝试几次，以及为什么只捕获ConnectionError。
- 能验证重新发现的工具名称和输入Schema版本仍兼容。
- 能说明写请求响应丢失后的结果不确定，不能照搬只读重试。

## 前置知识

真正先修是阶段28工具发现/调用与认证授权概念；阶段39 HTTP/API可帮助远程集成，未完成时仍可先学离线重试边界。

## 概念：只重试明确可重复的读取

远程调用失败可能是网络暂时断开，也可能是权限拒绝或输入错误。`call_read`只捕获`ConnectionError`，并最多调用`attempts`次；其他异常直接向调用者传播。这个边界很重要：对只读查询再试一次通常不会重复产生业务副作用，对“创建工单”盲目重试却可能创建两条记录。

下面摘录或简化本课示例的关键步骤，需结合[完整源码](examples/demo.py)中的定义与上下文阅读；运行时使用下方演示命令。

```python
for attempt in range(attempts):
    try:
        return operation()
    except ConnectionError:
        if attempt == attempts - 1:
            raise RemoteError("重连预算耗尽")
```

演示中的service第一次抛ConnectionError，第二次返回T1状态，因此输出attempts 2。`attempts=1`时第一次失败即用RemoteError结束；`attempts=0`在调用前由ValueError拒绝。另一个`compatible`检查远程服务是否实现所有必需工具，能力缺失时不应等到真实任务中才发现。

<details><summary>展开推导：operation第一次抛PermissionError，attempts=2时会调用几次？</summary>

只捕获ConnectionError，因此PermissionError不会进入重试分支，而是原样冒泡；operation只调用一次。若捕获所有Exception并重试，程序会把权限拒绝误当成网络抖动，造成重复请求或掩盖故障类型。
</details>

Java对照：HTTP客户端通常区分连接异常、超时、4xx与5xx；重试策略应结合方法语义、幂等键和总截止时间。当前夹具没有真实网络、认证令牌刷新或退避策略，不代表远程MCP集成完成。

## 演示文件与执行命令

默认工作目录是项目根目录 `C:\Users\Mason\Desktop\agent-study`。
如已创建虚拟环境，可以把python替换成 `.\.venv\Scripts\python.exe`，无需激活或修改执行策略。

```powershell
python lessons/29-mcp-remote/examples/demo.py
python lessons/29-mcp-remote/solutions/solution.py
python -m unittest discover -s lessons/29-mcp-remote/tests -v
```

第一条运行演示；第二条仅在完成练习后阅读与运行；第三条执行本阶段行为检查。
`-m`表示让解释器把模块当入口，`discover`搜寻test_开头文件，`-s`指定测试目录，`-v`显示每个测试名字。
测试正常时结尾是 `OK`。故意运行未完成的练习函数出现NotImplementedError，代表你还需要实现，不代表环境坏了。

### 默认演示预期输出

```text
{'ticket': 'T1', 'status': 'open'}
attempts 2
True
```

### 预期输出如何阅读

第一次只读调用模拟ConnectionError，第二次成功返回T1状态，因此尝试数为2。compatible随后确认必需get_ticket已发现。练习进一步比较Schema版本，避免工具名字不变但参数契约已经变化。

## 执行过程与状态变化

1. 第一次只读调用模拟断连。
2. 第二次成功，计数为2。
3. 身份失败直接传播，不进入断连重试。
4. 校验重新发现的工具是否满足所需能力。

默认operation第一次断连、第二次返回T1 open，因此attempts输出为2。随后compatible验证get_ticket确实仍被发现。

## 对照源码的逐行解释

按examples/demo.py中的顺序阅读，下列关键表达式决定正常与失败路径。

| 表达式或位置 | 为什么这样写及状态变化 |
|---|---|
| `range(attempts)` | attempts是总尝试数不是额外重试数；默认2意味着首次加一次重试。 |
| `except ConnectionError` | 只捕获可识别的断连，PermissionError立即传播；不要捕获所有Exception后继续循环。 |
| `RemoteError` | 最后一次失败转受控错误说明预算耗尽，调用者不能把它当空业务结果。 |
| `required与discovered集合差` | 所需工具不存在时失败；多出来工具不自动授权调用。 |
| `重新发现` | 建立新会话后重查工具名字和Schema，不能依赖断连前的陈旧缓存。 |
| `本机HTTP验证` | 自动验证脚本finally停止子进程，再尝试连接验证已断开；常驻服务只在手工集成命令里出现。 |
| `远程认证边界` | OAuth、TLS、token受众、scope和业务对象权限各有责任；本课回环服务未实现这些生产组件。 |

## Java Web对照

Java客户端也需限制重试异常类型和总次数；只读重放通常更安全，写响应丢失要靠幂等键或查询结果，不能把网络异常直接映射为空值。

## 易错点与排错顺序

1. 文件路径错误：确认终端在项目根目录，先运行演示而不是练习骨架。
2. 把空结果当成功：查返回状态与来源，不能编造缺失字段或证据。
3. 在失败后继续修改：先验证再变更，给失败输入补行为测试。
4. 共享可变对象：调用前后打印输入，确认是否被无意修改。
5. 把模拟效果当生产质量：检查本页边界说明与真实接入目录。
6. 只看最终回答：保留查询、状态或执行轨迹，定位失败发生在哪一步。

## 独立练习

发现时不仅比较名字，还比较输入Schema版本；模拟凭证失效只调用一次、读断连有限重试。说明写请求响应丢失为何不能照搬此函数。

打开 [练习要求](exercises/README.md)，在 [practice.py](exercises/practice.py) 实现。
骨架有意留下待实现函数，示例和参考答案不能替代你自己的思考与测试。
自动校验只证明离线重试和兼容规则；真实远程认证、Schema协商和连接生命周期仍需独立集成验收。

## 能力验收

- 能不看代码解释至少三个概念，并各举一个企业助手场景。
- 能预测演示执行前后的关键字段，再通过运行核对。
- 能独立修改一项业务规则并解释对结果的影响。
- 能让一个失败输入按预期被拒绝，且不产生越权或错误证据。
- 能说明本课测试证明了什么、没有证明什么。

材料制作、代码验证、学员掌握是三种状态；本课提供材料与验证方法，学员能力仍待验收。

## 工程延伸与边界

默认是断连控制的内存模拟，不实现远程MCP、OAuth或生产认证。integrations提供真实本机Streamable HTTP；本机验证不代表互联网部署安全。

从本课迁移到企业项目时，先写输入输出契约与独立评估案例，再决定存储、模型和框架。
保留可追溯来源和任务/身份信息，让问题能定位到具体数据与步骤。
添加性能优化前先检查正确性，尤其是失败时是否仍保护权限、预算和有效状态。
单元测试覆盖本地规则；真实网络、持久化、并发与供应商行为需要额外集成验证。

## 官方资料与复习

- [本课官方参考](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)：查API或协议边界，不要求一次读完。
- [Python 3.12教程](https://docs.python.org/zh-cn/3.12/tutorial/)：复习循环、函数、异常和模块。
- [本课知识卡](knowledge.md)：按定义、案例、误区整理。
- [验证记录](verification.md)：仅记录实际执行范围，不能据此声称生产部署通过。

## 真实集成入口

打开[集成说明](integrations/README.md)，按独立环境安装和验证；默认运行无需安装这些依赖。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 29`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
