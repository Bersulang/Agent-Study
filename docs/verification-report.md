# 全课程验证报告

验证日期：2026-10-06。环境：Windows PowerShell、Python 3.12.10。

## 验证方法

统一入口为`python tools/verify_course.py`：检查56阶段材料、教学源码编译、本地Markdown链接、默认演示、练习骨架、参考答案和标准库回归。机器可读结果写入忽略目录`artifacts/verification-report.json`。

默认案例与真实集成分开报告。练习骨架可以运行只代表材料可加载，所有学员能力仍待验收。

## 默认课程

最终完整运行已通过：56个阶段，256个Python文件，227份Markdown，219条运行与测试命令，163个标准库测试方法。源码语法、本地链接、默认演示、练习骨架和参考答案检查均通过。

重要回归覆盖参数校验、流式边界、权限、取消、共享状态冲突、协作预算、租约、审批、幂等、知识权限、恢复、发布门槛和路径边界。

## 真实集成

| 集成 | 版本与范围 | 实际结果 |
| --- | --- | --- |
| pypdf | 6.19.0，真实两页PDF夹具提取与空页识别 | 已通过 |
| LangGraph | 1.2.13，条件边、子图、Saver和中断批准/拒绝 | 已通过 |
| MCP stdio | 2.3.0，官方SDK客户端、工具/资源/提示与结构化输出 | 已通过 |
| MCP Streamable HTTP | 2.3.0，本机启动、发现、读取、关闭与断连 | 已通过 |
| A2A | a2a-sdk0.3.26，协议0.3，官方ClientFactory与本机HTTP | 已通过，不代表当前所有协议版本互通 |
| FastAPI | 0.115.12，TestClient业务、事件、隔离、取消；阶段39 | 已通过 |
| Java客户端探针 | Python→本机HTTP测试服务 | 已通过；不是Spring Boot联调 |
| OpenTelemetry | 1.45.0，真实SDK父子Span与内存导出 | 已通过，不连接OTLP后端 |
| Playwright | 1.63.0，真实Chromium、本地HTML与结果断言 | 已通过，不访问外部业务网站 |
| 毕业API | 实际FastAPI+SQLite、审批、重放、租户与输入校验 | 2个接口测试已通过 |
| 模型HTTP | 假Token、Mock契约及拒绝全部3xx | 已通过离线契约，未调用真实模型 |

阶段17/27/28/29的具体SDK命令及依赖快照见对应integrations/verification.md；阶段30—43的详细集成记录见 [验证记录](../lessons/30-routing-roles/verification.md)。

根代理另外实际执行：

```powershell
.\.venv-integrations\Scripts\python.exe lessons/46-observability/integrations/otel_demo.py
.\.venv-integrations\Scripts\python.exe lessons/55-browser-multimodal/integrations/browser_demo.py
& "$env:TEMP/agent-study-services-venv/Scripts/python.exe" lessons/56-capstone/integrations/test_api.py -v
```

其中`.venv-integrations`安装本课锁定的OpenTelemetry/Playwright，Chromium通过官方安装命令下载；临时API环境依赖与阶段39一致。环境目录均不提交。

## 审查中修复的边界

- 模型适配默认urllib重定向可能把认证头带到其它主机或HTTP；已先复现，再在跳转前拒绝全部3xx并回归。
- SQLite事务上下文不会关闭连接；备份/恢复用closing释放句柄，验证Windows清理。
- 不存在的备份源会被普通connect创建为空库；已改存在性检查和只读打开，恢复检查业务Schema并禁止覆盖已有目标。
- 参考答案补齐错误和边界案例；writer权限与可信审批分开；数据目录无效或不可写时在监听之前拒绝启动。
- 毕业项目补新知识/只读工具、模型计划Schema、参数修改后的重新审批和交付手册。

## 未验证环境

- 未调用付费或远程真实模型，未测真实模型准确率、账单与供应商限流。
- 未下载Embedding/图像/语音模型，未验证真实识别或转写质量。
- 本机缺JDK/Maven，未构建Spring Boot或运行Java测试，也未Python→Spring端到端联调。
- 本机缺Docker，未运行镜像、Compose、容器沙箱或重启持久卷演练。
- 未验证生产OAuth/JWT提供方、TLS、公网协议互操作、分布式队列、企业负载或外部业务副作用。
- GitHub Actions文件已提供；Windows/Linux托管运行需要你推送到自己的仓库后执行。

以上环境都有课程说明或集成文件，但未执行的项目不标为通过。课程完整交付不表示对任何企业场景作通用生产保证。
