# 阶段39知识：FastAPI服务与事件接口

## 关联

[课程讲义](README.md) · [运行示例](examples/demo.py) · [练习](exercises/README.md)

## 概念与业务落点

### 请求校验

在入口验证类型、字段与范围，失败不创建任务。

空prompt返回422，领域层任务数不增加。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 会话与任务

会话组织多轮对话，任务表示一次有限执行，不应混用id。

create接收session_id并生成task-1。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 事件流

progress描述进度、text描述增量内容、final表示正式完成。

StreamingResponse发送SSE，支持after序号续读。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 取消

把任务状态转为canceled，后续advance不得追加final。

cancel案例事件只有progress和canceled。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

## 状态与失败路径

- TaskService是领域层，默认程序不需要第三方依赖。
- create验证后才生成id并写tasks。
- advance仅处理running任务，因此取消后不生成最终结果。
- read返回events拷贝，调用者不能通过列表引用篡改事件。
- integrations app用路由装饰器注册接口，TestClient在进程内真实调用ASGI应用。

## 易错解释

- 把text当最终结果触发业务写入：要等待明确final。
- 每次重连创建新任务：会重复执行，应复用task id与事件序号。
- BackgroundTasks当可靠队列：进程退出会丢任务。

## Java对照

FastAPI路径装饰器类似Spring的@RequestMapping，Pydantic类似Bean Validation；Python注解由框架读取校验，普通函数注解不会自动校验。

## 独立迁移

实现会话隔离和事件续读：session不匹配拒绝；after为已收到序号，只返回后续事件；负序号拒绝。

## 工程限制

集成页面仅供本地教学；生产还需要真实用户身份、持久事件日志、背压、代理缓冲设置与Worker队列。

默认行为是教学机制，不等于模型质量证明或生产系统认证。验收必须由学员独立完成并提供证据。
