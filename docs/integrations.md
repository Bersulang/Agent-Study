# 真实接入与环境边界

默认56阶段案例和标准库回归不需要密钥或网络。真实接入单独安装并手动执行，防止离线检查产生业务副作用或费用。

## 机制验收与集成验收

每个关卡分两层记录：**机制验收**使用固定输入、模拟模型或测试服务，检查控制逻辑、失败路径和数据契约；**集成验收**使用目标模型/服务/运行环境，检查真实调用、认证、用量、故障与运行证据。只有两层都满足当前阶段要求，才能记录为完整通过。

外部环境缺失时可以先完成机制验收并继续无依赖课程，状态记为“机制已通过，集成待验收”。不得把待验收写成已通过，也不要用模拟数据冒充真实质量、性能或认证结果。本文所列接入入口当前是否实测，以阶段进度表和验证报告中的本次执行记录为准。

| 关卡 | 机制验收 | 集成验收及证据 |
| --- | --- | --- |
| 08 模型文本API | 请求/响应解析、超时/认证错误、用量字段缺失和错误脱敏的离线契约测试 | 对已获准模型发真实文本请求；记录模型ID、时间、请求/响应轮次和实际用量。现有适配器只支持文本，不支持原生工具调用内容块。 |
| 13 Agent反馈循环 | 模拟模型读取工具观测并改变动作；未知工具、工具拒绝、预算终止和轨迹关联测试 | 若阶段目标包含真实模型工具循环，证明多轮模型决策、tool call关联ID、观测回传、未知工具/失败处理、停止预算和真实用量；不能把08文本适配器当成tool calling已实现。 |
| 18 RAG | 固定文档与向量/相似度夹具验证引用结构、无证据拒答、权限过滤 | 使用真实Embedding模型或本地Embedding服务建索引并检索真实授权资料；记录模型/服务版本、查询、向量维度和可定位引用。 |
| 39 API服务 | 路由/参数/事件契约、非法请求无副作用、取消与状态测试 | 启动真实FastAPI应用和TestClient/HTTP客户端，记录任务创建、事件、取消及重连结果；此关完成后阶段37才能执行远程服务专项。 |
| 40 Java业务集成 | Python侧契约模拟、401/403/超时映射、身份不能由请求参数篡改 | 启动真实Spring Boot与Python服务，记录身份传递、权限拒绝和调用追踪；缺少Java环境则挂起集成项。 |
| 49 部署 | 配置校验、健康状态、错误启动与离线部署文件检查 | 在目标容器/干净环境构建并启动，核验就绪状态、依赖失败和恢复；记录镜像/配置版本与命令。 |
| 56 毕业 | 固定回归、审批/幂等/恢复机制、质量阈值和交付文档检查 | 用真实模型/身份/持久队列与目标部署演示毕业验收矩阵。按场景预填质量、延迟、成本阈值并附原始证据；缺环境项标记待验收。 |

离线机制验收不自动为后续阶段授权“完整通过”。连续主项目各关卡的增量成果见[项目里程碑](milestones.md)。

## 接入入口

| 阶段 | 真实接入 | 安装与运行 |
| --- | --- | --- |
| 06 | pytest、ruff、mypy工程工具 | [开发工具说明](../lessons/06-async-testing/integrations/README.md) |
| 08 | HTTPS模型文本调用，3xx默认拒绝 | [模型HTTP说明](../lessons/08-model-api/integrations/README.md) |
| 17 | pypdf真实PDF解析，OCR边界 | [文档接入](../lessons/17-document-ingestion/integrations/README.md) |
| 18 | Ollama Embedding与本地SentenceTransformer | [Embedding接入](../lessons/18-basic-rag/integrations/README.md) |
| 27 | 真实LangGraph、子图、Saver和中断 | [框架接入](../lessons/27-langgraph/integrations/README.md) |
| 28 | 官方MCP stdio客户端与服务端 | [本地MCP](../lessons/28-mcp-local/integrations/README.md) |
| 29 | 官方MCP Streamable HTTP | [远程MCP](../lessons/29-mcp-remote/integrations/README.md) |
| 37 | 官方A2A SDK与HTTP客户端 | [A2A说明](../lessons/37-a2a-remote/integrations/README.md) |
| 39 | FastAPI、TestClient和交互页面 | [API说明](../lessons/39-fastapi-service/integrations/README.md) |
| 40 | Spring Boot、JUnit及Python客户端 | [Java集成](../lessons/40-java-integration/integrations/README.md) |
| 46 | OpenTelemetry真实SDK内存导出 | [追踪接入](../lessons/46-observability/integrations/README.md) |
| 49 | HTTP健康服务与Docker Compose | [部署接入](../lessons/49-deployment/integrations/README.md) |
| 54 | 执行沙箱限制与只读SQL | [隔离边界](../lessons/54-coding-data-project/integrations/README.md) |
| 55 | Playwright、Ollama图像、faster-whisper语音 | [多模态接入](../lessons/55-browser-multimodal/integrations/README.md) |
| 56 | 完整毕业FastAPI与模型计划适配 | [毕业API](../lessons/56-capstone/integrations/README.md) |

## 依赖策略

本机保留`.venv`用于日常课程，默认课程只需Python标准库。需要真实接入时，按对应课程安装依赖；虚拟环境目录不提交Git。

每课requirements固定本次验证或核查的直接依赖；SDK环境快照记录实测环境。直接依赖固定不等于所有传递依赖永远不变，长期维护需要生成锁文件、复测与安全更新。

不同阶段的MCP和A2A教材固定了不同协议/SDK版本，不把它们混成一个全局环境。后续升级先读迁移文档，再运行对应契约与集成测试。

Windows示例可为某一阶段创建独立环境：

```powershell
python -m venv .venv-sdk
.\.venv-sdk\Scripts\python.exe -m pip install -r lessons/27-langgraph/integrations/requirements.txt
.\.venv-sdk\Scripts\python.exe lessons/27-langgraph/integrations/langgraph_demo.py
```

实际文件名称以对应集成README为准。没有密钥、模型、Java或Docker时，不要把未运行项写成成功；先完成默认离线学习再接入。

## 密钥与数据

根目录的[.env.example](../.env.example)列出代码实际使用的配置名。可用`Copy-Item .env.example .env`创建本地配置记录；`.env`被Git忽略，模板可提交。

**当前代码不会自动读取`.env`。** `os.environ`读取的是启动Python进程时继承的环境变量。把值写进文件不会自动设置这些变量；目前按[阶段08配置步骤](../lessons/08-model-api/integrations/README.md)在PowerShell中设置`$env:MODEL_BASE_URL`、`$env:MODEL_NAME`和`$env:MODEL_API_KEY`后运行。非敏感配置例如`$env:PORT = '8080'`也采用同样方式。设置仅作用于当前终端及其启动的子进程，关闭终端后失效。

不上传真实.env、SSH文件、模型密钥、业务数据库、Cookie或敏感媒体。真实模型调用只在显式设置环境并执行集成脚本时发生。演示夹具不作为真实模型质量、安全认证或企业负载结论。
