# 阶段28知识卡：本地MCP接入

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

## Host与Client与Server

- 定义：宿主管理交互，客户端维持会话，服务器提供能力。
- 场景例子：宿主中的客户端连接工单服务。
- 判断方法：观察输入、输出和失败分支，不能只看是否打印成功。
- 复习问题：去掉这一机制会导致什么错误？
- 演示关联：examples/demo.py的核心处理函数与tests/test_behavior.py。

## Tools

- 定义：可被调用的带参数操作。
- 场景例子：get_ticket(ticket_id)。
- 判断方法：观察输入、输出和失败分支，不能只看是否打印成功。
- 复习问题：去掉这一机制会导致什么错误？
- 演示关联：examples/demo.py的核心处理函数与tests/test_behavior.py。

## Resources与Prompts

- 定义：资源提供数据，提示提供可复用消息模板。
- 场景例子：policy://current与summarize_ticket。
- 判断方法：观察输入、输出和失败分支，不能只看是否打印成功。
- 复习问题：去掉这一机制会导致什么错误？
- 演示关联：examples/demo.py的核心处理函数与tests/test_behavior.py。

## stdio生命周期

- 定义：子进程通过标准输入输出交换协议消息。
- 场景例子：stdout不能混入调试日志。
- 判断方法：观察输入、输出和失败分支，不能只看是否打印成功。
- 复习问题：去掉这一机制会导致什么错误？
- 演示关联：examples/demo.py的核心处理函数与tests/test_behavior.py。

## 实现与真实系统的差别

默认dispatch不是完整MCP也不是JSON-RPC实现。integrations使用官方Python SDK启动真实stdio子进程与会话。

## 调试方法

1. 缩小到一个输入，写出预期结果。
2. 跟踪本课trace或状态字段。
3. 检查错误发生在输入、控制还是输出边界。
4. 补失败案例并复跑测试。

## 验收关联

练习要求：为工具调用添加请求级错误结果：未知方法、未知工具与非法参数应区分错误码；不能把异常堆栈作为正文返回。用真实SDK客户端完成发现、资源读取和提示获取。

能定义、修改、排错和验证才构成掌握，课程交付不是学员通过。
