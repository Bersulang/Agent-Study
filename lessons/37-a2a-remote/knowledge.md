# 阶段37知识：跨服务Agent与A2A

## 关联

[课程讲义](README.md) · [运行示例](examples/demo.py) · [练习](exercises/README.md)

## 概念与业务落点

### Agent Card

远程Agent发布的能力与传输元数据，不是授权凭据。

集成服务声明ticket-status技能和JSON-RPC端点。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### Task生命周期

任务有id、上下文和状态，状态不能任意倒退。

submitted到completed，或submitted到canceled；终态不再执行。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 消息与产物

消息承载交互，Artifact是任务产生的正式输出。

SDK executor通过TaskUpdater添加T-7工单状态文本产物。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 协议与认证

A2A标准规定交互对象与方法，认证/授权仍由服务边界实现。

integrations使用官方a2a-sdk==0.3.26；默认TaskRegistry只是领域教具。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

## 状态与失败路径

- submit保存任务，重复id被拒绝。
- finish检查submitted，再经历working并写artifact。
- cancel只允许未完成任务，取消后finish不做写入。
- get对未知id给结构化错误。
- 真实协议集成让SDK处理JSON-RPC封装与状态存储，不能把本地字典叫A2A实现。

## 易错解释

- 把自定义POST /agent叫A2A：接口名字不能证明协议兼容。
- Agent Card技能声明等于权限：调用时仍要鉴权。
- 宣称已取消就证明远程副作用没发生：必须定义任务与业务取消边界。

## Java对照

类似Java远程服务发现加长任务接口，但A2A还标准化消息parts、task与artifact；Python SDK类型使用camelCase JSON别名。

## 独立迁移

封装取消为结构化响应：未知任务not_found、终态not_cancelable、可取消任务canceled；不能对completed任务删除产物。

## 工程限制

教材固定协议0.3以复现API；最新1.x存在迁移差异。跨企业连接需HTTPS、可信发现、授权和SSRF边界；内存store不支持重启。

默认行为是教学机制，不等于模型质量证明或生产系统认证。验收必须由学员独立完成并提供证据。
