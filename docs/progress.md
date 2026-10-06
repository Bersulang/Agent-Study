# 学习进度与验收记录

## 当前状态

- 当前学习阶段：**01：开发环境与运行机制**。
- 材料状态：已准备。
- 练习状态：未提交。
- 能力状态：待验收。
- 阶段 01—56：全部讲义、知识、示例、练习与答案已准备；所有能力仍待验收。
- 最近维护日期：2026-10-06。

## 本机环境检查

| 项目 | 实际结果 | 说明 |
| --- | --- | --- |
| 系统终端 | Windows PowerShell | 文档按该环境编写 |
| Python | 3.12.10 | 当前已安装，无需重新安装 |
| pip | 25.0.1 | 已安装，本阶段不下载第三方包 |
| uv | 0.12.23 | 已安装，本阶段先理解 venv 和 pip |
| Git | 2.56.0.windows.1 | 已初始化本地 main 分支，作者配置仅作用于当前项目 |

## 阶段 01 能力检查

以下由你的操作和解释验收，助手运行示例不能代替你的验收。

- [ ] 能区分终端、Python 解释器、编辑器与程序文件。
- [ ] 能从项目根目录独立运行指定脚本。
- [ ] 能创建虚拟环境，并确认实际使用的解释器。
- [ ] 能说明虚拟环境解决什么问题，以及它不隔离什么。
- [ ] 能独立修改启动信息并运行。
- [ ] 能定位路径错误，并区分终端命令和 Python 代码。
- [ ] 能在编辑器中选对解释器，使用断点观察执行顺序。
- [ ] 能说明 Git 工作区、暂存区和提交的作用。

## 阶段 01 首次交付验证（历史记录）

验证目标是保证课程命令和示例可用，以下结果由助手在本机实际执行获得，不作为你的能力验收依据。

| 验证 | 状态 |
| --- | --- |
| 项目虚拟环境创建与解释器确认 | 已通过：Python 3.12.10，解释器指向本项目 `.venv`，虚拟环境判断为 True |
| 两个演示脚本运行 | 已通过：启动信息和环境信息与讲义相符 |
| 练习初始模板与参考答案运行 | 已通过：模板输出待填写提示，答案输出四行；未替学员完成练习 |
| Python 语法检查 | 已通过：4 个 Python 文件 |
| Markdown 本地链接与阶段编号检查 | 已通过：10 份 Markdown、29 个本地链接，阶段 01—56 连续且唯一 |

实际运行命令（项目根目录）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe .\lessons\01-environment\examples\hello_agent.py
.\.venv\Scripts\python.exe .\lessons\01-environment\examples\environment_info.py
.\.venv\Scripts\python.exe .\lessons\01-environment\exercises\startup_card.py
.\.venv\Scripts\python.exe .\lessons\01-environment\solutions\startup_card.py
```

另使用 Python 标准库编译全部教学源码，检查 Markdown 本地链接目标、代码围栏配对和阶段编号。编辑器断点和 Git 初始化留给你的操作练习，本批没有声称已经完成这些交互验证。

## 个人问题与反馈

目前尚未收到练习提交，不预填你的个人错误。

后续记录格式：问题 → 现象 → 原因 → 修复 → 再次验证 → 知识条目链接。

## 下一步

阅读 [阶段 01 讲义](../lessons/01-environment/README.md)，运行演示，独立完成 [启动卡片练习](../lessons/01-environment/exercises/startup_card.py)，填写 [验收提交表](../lessons/01-environment/exercises/submission.md)。

## 全课程交付与能力状态

| 阶段 | 课程 | 材料 | 练习 | 能力 |
| --- | --- | --- | --- | --- |
| 01 | [开发环境与第一个企业助手程序](../lessons/01-environment/README.md) | 已准备 | 未提交 | 待验收 |
| 02 | [变量、容器与可变性](../lessons/02-basic-syntax/README.md) | 已准备 | 未提交 | 待验收 |
| 03 | [函数、作用域与模块](../lessons/03-functions-modules/README.md) | 已准备 | 未提交 | 待验收 |
| 04 | [文件、JSON与异常边界](../lessons/04-files-errors/README.md) | 已准备 | 未提交 | 待验收 |
| 05 | [类型、对象与SDK常见语法](../lessons/05-types-objects/README.md) | 已准备 | 未提交 | 待验收 |
| 06 | [异步、超时、取消与测试](../lessons/06-async-testing/README.md) | 已准备 | 未提交 | 待验收 |
| 07 | [需求边界与可验收目标](../lessons/07-requirements/README.md) | 已准备 | 未提交 | 待验收 |
| 08 | [模型API、上下文与成本](../lessons/08-model-api/README.md) | 已准备 | 未提交 | 待验收 |
| 09 | [提示词结构、版本与评估](../lessons/09-prompt-engineering/README.md) | 已准备 | 未提交 | 待验收 |
| 10 | [结构化输出、SSE与取消](../lessons/10-structured-streaming/README.md) | 已准备 | 未提交 | 待验收 |
| 11 | [工具契约与参数校验](../lessons/11-tool-contracts/README.md) | 已准备 | 未提交 | 待验收 |
| 12 | [重试、幂等与不确定结果](../lessons/12-tool-reliability/README.md) | 已准备 | 未提交 | 待验收 |
| 13 | [手写模型—工具循环](../lessons/13-agent-loop/README.md) | 已准备 | 未提交 | 待验收 |
| 14 | [消息、事件与最小Runtime](../lessons/14-agent-runtime/README.md) | 已准备 | 未提交 | 待验收 |
| 15 | [工作流、依赖与有限重规划](../lessons/15-workflow-planning/README.md) | 已准备 | 未提交 | 待验收 |
| 16 | [澄清、审批与结果检查](../lessons/16-human-review/README.md) | 已准备 | 未提交 | 待验收 |
| 17 | [文档导入与质量检查](../lessons/17-document-ingestion/README.md) | 已准备 | 未提交 | 待验收 |
| 18 | [带引用的基础RAG](../lessons/18-basic-rag/README.md) | 已准备 | 未提交 | 待验收 |
| 19 | [检索优化与定位失败](../lessons/19-retrieval-optimization/README.md) | 已准备 | 未提交 | 待验收 |
| 20 | [知识生命周期](../lessons/20-knowledge-lifecycle/README.md) | 已准备 | 未提交 | 待验收 |
| 21 | [知识权限与冲突](../lessons/21-knowledge-permissions/README.md) | 已准备 | 未提交 | 待验收 |
| 22 | [受预算控制的Agentic RAG](../lessons/22-agentic-rag/README.md) | 已准备 | 未提交 | 待验收 |
| 23 | [上下文工程](../lessons/23-context-engineering/README.md) | 已准备 | 未提交 | 待验收 |
| 24 | [长期记忆的来源与修正](../lessons/24-long-term-memory/README.md) | 已准备 | 未提交 | 待验收 |
| 25 | [工作空间与任务恢复](../lessons/25-workspace-tasks/README.md) | 已准备 | 未提交 | 待验收 |
| 26 | [按需加载的能力包](../lessons/26-skills/README.md) | 已准备 | 未提交 | 待验收 |
| 27 | [LangGraph状态与中断](../lessons/27-langgraph/README.md) | 已准备 | 未提交 | 待验收 |
| 28 | [本地MCP接入](../lessons/28-mcp-local/README.md) | 已准备 | 未提交 | 待验收 |
| 29 | [远程MCP与故障边界](../lessons/29-mcp-remote/README.md) | 已准备 | 未提交 | 待验收 |
| 30 | [职责划分与路由](../lessons/30-routing-roles/README.md) | 已准备 | 未提交 | 待验收 |
| 31 | [主控与子Agent委派](../lessons/31-supervisor-workers/README.md) | 已准备 | 未提交 | 待验收 |
| 32 | [Handoff控制权交接](../lessons/32-handoff/README.md) | 已准备 | 未提交 | 待验收 |
| 33 | [并行任务与依赖](../lessons/33-parallel-dependencies/README.md) | 已准备 | 未提交 | 待验收 |
| 34 | [通信契约与共享状态](../lessons/34-contracts-state/README.md) | 已准备 | 未提交 | 待验收 |
| 35 | [生成检查与证据冲突](../lessons/35-review-conflicts/README.md) | 已准备 | 未提交 | 待验收 |
| 36 | [协作失败与总预算](../lessons/36-failure-budgets/README.md) | 已准备 | 未提交 | 待验收 |
| 37 | [跨服务Agent与A2A](../lessons/37-a2a-remote/README.md) | 已准备 | 未提交 | 待验收 |
| 38 | [架构评估与选择](../lessons/38-architecture-evaluation/README.md) | 已准备 | 未提交 | 待验收 |
| 39 | [FastAPI服务与事件接口](../lessons/39-fastapi-service/README.md) | 已准备 | 未提交 | 待验收 |
| 40 | [Spring Boot契约与身份](../lessons/40-java-integration/README.md) | 已准备 | 未提交 | 待验收 |
| 41 | [持久化、事务与恢复](../lessons/41-persistence/README.md) | 已准备 | 未提交 | 待验收 |
| 42 | [Worker队列与租约](../lessons/42-workers-queues/README.md) | 已准备 | 未提交 | 待验收 |
| 43 | [审批、幂等与查证](../lessons/43-approval-idempotency/README.md) | 已准备 | 未提交 | 待验收 |
| 44 | [评估数据与质量标准](../lessons/44-evaluation-data/README.md) | 已准备 | 未提交 | 待验收 |
| 45 | [执行过程与回归测试](../lessons/45-trajectory-tests/README.md) | 已准备 | 未提交 | 待验收 |
| 46 | [链路追踪、成本与脱敏](../lessons/46-observability/README.md) | 已准备 | 未提交 | 待验收 |
| 47 | [提示注入、工具边界与沙箱](../lessons/47-injection-sandbox/README.md) | 已准备 | 未提交 | 待验收 |
| 48 | [身份、最小权限与多租户隔离](../lessons/48-identity-tenancy/README.md) | 已准备 | 未提交 | 待验收 |
| 49 | [部署、配置与健康检查](../lessons/49-deployment/README.md) | 已准备 | 未提交 | 待验收 |
| 50 | [版本、发布门槛与回滚](../lessons/50-version-release/README.md) | 已准备 | 未提交 | 待验收 |
| 51 | [性能、成本与容量治理](../lessons/51-capacity-cost/README.md) | 已准备 | 未提交 | 待验收 |
| 52 | [备份恢复、事故与反馈闭环](../lessons/52-operations-recovery/README.md) | 已准备 | 未提交 | 待验收 |
| 53 | [多 Agent 调研助手项目](../lessons/53-research-project/README.md) | 已准备 | 未提交 | 待验收 |
| 54 | [受控编码与数据分析助手项目](../lessons/54-coding-data-project/README.md) | 已准备 | 未提交 | 待验收 |
| 55 | [浏览器与多模态助手项目](../lessons/55-browser-multimodal/README.md) | 已准备 | 未提交 | 待验收 |
| 56 | [企业知识与工单协作助手：毕业交付](../lessons/56-capstone/README.md) | 已准备 | 未提交 | 待验收 |

完整代码验证与外部环境边界见 [全课程验证报告](verification-report.md)。当前学习阶段仍为01；不要因材料完成直接跳过验收。
