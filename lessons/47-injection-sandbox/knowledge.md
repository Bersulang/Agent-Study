# 阶段 47 知识：提示注入、工具边界与沙箱

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

### 1. 间接提示注入

攻击指令可能来自网页、PDF或工具结果。检索到的数据没有资格授予权限；模型的意图与执行器的授权判定分离。关键词检测无法保证发现全部变体。

### 2. 能力与默认拒绝

工具只暴露允许的动作，调用前校验用户、参数与范围。路径以resolve后的实际位置检查，不能只用字符串startsWith。Java服务同样应在后端验证资源权限。

### 3. 沙箱与纵深防御

工作目录检查不是操作系统沙箱，超时也不是完整隔离。真正执行不可信代码需要进程/容器隔离、资源与网络限制、只读挂载和独立身份，不能让模型任意启动shell。

## 执行过程

入口先检查动作是否在只读白名单，再把相对路径解析到工作空间；使用relative_to验证真实路径归属；网络例子只允许精确HTTPS来源，不进行真实请求；网页内容无论写了什么都不能改变这层权限。

## 新语法

`Path.resolve()` 解析实际路径；relative_to要求目标在指定目录内；raise ... from ...保存错误因果；urlsplit解析URL而非靠字符串包含判断。

## 判断与排错

| 恶意文档覆盖规则 | 把检索内容拼成高权限指令 | 标注不可信数据并在工具层硬性授权 |
| 路径前缀相似绕过 | 直接做字符串前缀判断 | 解析实际路径并检查目录归属 |
| 容器仍可读宿主凭证 | 挂载或权限范围过大 | 只读最小挂载、非root、无网络、资源限制 |

## 工程边界

这只是能力边界演示，路径检查存在检查与使用之间的竞态（TOCTOU）。生产使用隔离文件系统与不可变挂载；网络需出口代理、DNS/IP和重定向策略；[阶段54受限执行说明](../54-coding-data-project/integrations/README.md)提供容器约束建议；本阶段没有独立integrations目录，本机未运行Docker。

## 复习问题

用恶意内容说明“检测注入”与“阻止未授权操作”的区别；不能把路径检查称为生产沙箱；验证失败条件。

## 资料

- [OWASP提示注入防护](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)。
- [Python pathlib](https://docs.python.org/3.12/library/pathlib.html)。

## 练习扩展与新验证边界

[完整边界案例](solutions/solution.py)覆盖绝对路径、目录、后缀、HTTPS与端口。DNS、重定向与TOCTOU见[参考解释](solutions/README.md)，本阶段没有独立集成目录；隔离建议关联[54集成](../54-coding-data-project/integrations/README.md)。

对应实现与完整失败案例见[参考答案说明](solutions/README.md)，完成练习后再阅读。
