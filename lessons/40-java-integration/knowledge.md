# 阶段40知识：Spring Boot契约与身份

## 关联

[课程讲义](README.md) · [运行示例](examples/demo.py) · [练习](exercises/README.md)

## 概念与业务落点

### 服务身份

证明调用方服务是谁，与用户权限不同。

X-Service-Token固定本地示例值只供教学。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 用户委派

服务请求携带用户身份线索，业务服务仍要核验。

Java通过服务端user目录确定alice所属acme，而非相信任意X-Tenant。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 跨语言契约

双方统一JSON字段、错误对象与状态码，不能依赖Python对象布局。

ticket和trace为字符串，状态200/401/403/404明确区分。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

### 超时与追踪

请求有限等待并传递关联标识，失败能定位到调用链。

Python urlopen(timeout=2)发送X-Trace-Id。

阅读示例时找到实现此约定的条件或状态转换，再描述删除它会造成的错误。

## 状态与失败路径

- 离线authorize_call演示两层验证，先检查服务token。
- 其次比较租户和scope，拒绝请求没有业务结果。
- json.dumps/loads保证交换数据采用语言无关结构。
- integrations Java控制器在服务端固定用户目录核查权限。
- Python client分别捕获HTTPError和网络错误，不把所有失败都归为模型回答不好。

## 易错解释

- 相信调用方传来的tenant即权限：应从已验证身份解析授权。
- 401和403混用：分别是身份无法验证与身份权限不足。
- Python调用超时后无条件重发写操作：服务可能已提交。

## Java对照

用户已有Java Web经验，本课重点是Python urllib、异常处理和JSON；Java record为不可变传输对象，Python dict默认可变。

## 独立迁移

将401标为authentication、403为authorization、404为not_found、429/503为retryable_read，其他为permanent；只读重试不代表写入安全。

## 工程限制

真实环境使用TLS、OAuth2/JWT或mTLS并验证签名、audience、期限及scope；固定token和内存用户目录不是生产认证。

默认行为是教学机制，不等于模型质量证明或生产系统认证。验收必须由学员独立完成并提供证据。
