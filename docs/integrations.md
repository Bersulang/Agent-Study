# 真实接入与环境边界

默认56阶段案例和标准库回归不需要密钥或网络。真实接入单独安装并手动执行，防止离线检查产生业务副作用或费用。

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

不上传真实.env、SSH文件、模型密钥、业务数据库、Cookie或敏感媒体。真实模型调用只在显式设置环境并执行集成脚本时发生。演示夹具不作为真实模型质量、安全认证或企业负载结论。
