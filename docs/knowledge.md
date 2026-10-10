# Agent 开发知识手册

本文件随课程和你的提问持续维护。它保存可复习的概念与经验，具体操作过程见各阶段讲义。基础条目与全部56阶段的知识文档已交付；后续课堂问题和作业反馈继续维护。

## 项目配置补充：虚拟环境与环境变量

### 练习自动校验、断言与结果范围

`python tools/check_exercise.py 01`使用预设输入检查学员的练习代码；失败提示是定位问题的依据。断言表示“预期这个条件成立”，与Java测试中的assertEquals/assertTrue用途相近。检查器不调用参考答案代替作业，空测试或仅打印“完成”不能代表通过。

结果自动记录，代码和校验规则的指纹变化后需要重新检查。代码检查通过只证明已覆盖行为，不能证明真实模型质量或全部课程能力。关联：[自动校验操作](exercise-checks.md)、[阶段01练习](../lessons/01-environment/exercises/startup_card.py)、[统一检查入口](../tools/check_exercise.py)。

- `.venv`保存日常课程的Python解释器与依赖，不提交Git。可选SDK按对应课程需要安装，类似为Java项目管理依赖集合。
- `.env.example`是可提交的配置模板，`.env`是被忽略的本地配置文件。当前脚本只读进程环境变量，不能把它等同于Spring Boot自动加载的配置文件。

操作与配置名见[集成说明](integrations.md)。

## K001：终端、解释器、编辑器和脚本

**定义：** 终端提供输入命令的界面；PowerShell 负责理解终端中的命令。Python 解释器执行 Python 代码；编辑器用于编辑文件；`.py` 文件保存程序源代码。

**最小例子：** 在 PowerShell 中输入 `python --version`，查看解释器版本。输入 `python path\hello.py`，让解释器执行文件。

**Java 对照：** 可以先用“运行时执行源程序”建立联系。Java 常见流程是编译为字节码，再由 JVM 运行；Python 也有编译与字节码机制，不能简单理解为完全没有编译。

**易错点：** `>>>` 是 Python 交互模式提示符。在那里不能直接输入 PowerShell 的文件运行命令。使用 `exit()` 返回终端。

关联：[阶段 01：运行方式](../lessons/01-environment/README.md)。来源：[Python 解释器文档](https://docs.python.org/zh-cn/3.12/tutorial/interpreter.html)。

## K002：当前工作目录与文件路径

**定义：** 相对路径通常相对于程序启动时的当前工作目录解释；绝对路径写出完整位置。工作目录与脚本所在目录不一定相同。

**例子：** `Get-Location` 查看 PowerShell 当前目录；`cd C:\Users\Mason\Desktop\agent-study` 切换到项目根目录。`Test-Path .\lessons\01-environment\examples\hello_agent.py` 检查文件存在。

**Java 对照：** 类似 Java 程序中的工作目录概念，不等于某个源文件或 class 文件所在位置。

**易错点：** 找不到脚本先查目录和路径，不急着重装 Python。含空格的可执行文件路径在 PowerShell 中可用 `& "完整路径"` 调用。

关联：[阶段 01：路径排查](../lessons/01-environment/README.md)。

## K003：虚拟环境与依赖

**定义：** 虚拟环境为项目提供独立的 Python 运行入口与第三方包安装位置。不同项目可以拥有不同的依赖集合。

**创建：** `python -m venv .venv`。

**运行：** `.\.venv\Scripts\python.exe .\lessons\01-environment\examples\hello_agent.py`。

**确认：** `.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"`。结果应指向本项目 `.venv\Scripts\python.exe`。

**Java 对照：** 它解决的是项目运行环境与依赖隔离问题，和 Maven 的部分用途有联系，但不等价。虚拟环境不会自动保存依赖版本清单，也不等同于容器。

**易错点：** 虚拟环境不是安全沙箱，不限制文件或网络权限。激活只是修改当前终端的命令查找环境；指定解释器完整路径也可以运行。

关联：[阶段 01：虚拟环境](../lessons/01-environment/README.md)。来源：[Python 虚拟环境文档](https://docs.python.org/zh-cn/3.12/tutorial/venv.html)。

## K004：`-m`、`-c` 与 pip

**`-m`：** 让 Python 运行指定模块，例如 `python -m venv .venv`。模块可以先理解为可供 Python 使用的代码单元。

**`-c`：** 让 Python 执行命令后提供的一段代码；适合简短检查，多行程序保存为文件更清楚。

**pip：** Python 的包安装工具。使用 `.\.venv\Scripts\python.exe -m pip --version`，能明确检查的是哪个解释器对应的 pip。

**易错点：** 裸用 `pip` 可能安装到另一环境。安装成功但导入失败时，先核对安装与运行使用的解释器。当前阶段没有第三方依赖，不需要安装框架。

关联：[阶段 01：依赖管理](../lessons/01-environment/README.md)。

## K005：字符串、输出与注释

**定义：** 引号包围的内容是字符串；`print(...)` 调用输出功能；`#` 后面的内容是注释，不作为代码执行。

```python
# 注释说明下面这行输出的用途。
print("企业知识与工单助手")
```

**Java 对照：** `print(...)` 可与 `System.out.println(...)` 对照理解。Python 调用函数不需要给这行添加分号。

**易错点：** 代码中的引号和括号使用英文符号；中文文字可以放在字符串与注释中。删除字符串的引号后，程序会尝试把内容理解成名字等代码，可能产生名称错误或语法错误。

关联：[第一个示例](../lessons/01-environment/examples/hello_agent.py)。

## K006：读取运行环境

**概念：** `import` 导入模块；`sys.executable` 是当前解释器路径；`sys.prefix` 是当前环境前缀；`sys.base_prefix` 是基础环境前缀。在常规 venv 中，后两者不同可帮助确认虚拟环境。

`platform.python_version()` 返回 Python 版本，`Path.cwd()` 返回当前工作目录。括号表示调用，点号用于访问模块或对象中的成员；对象机制后续课程再展开。

**易错点：** 机器上安装了某个 Python，不代表编辑器使用的就是它；以实际解释器路径为依据。

关联：[环境信息示例](../lessons/01-environment/examples/environment_info.py)。

## K007：断点与调试

**定义：** 断点让程序在指定位置暂停。逐步执行可以观察执行顺序；后续课程使用变量面板观察数据变化。

**本课操作：** 在第一条 `print` 设置断点，选择 `.venv` 解释器，启动 Python 文件调试，观察程序依次输出。

**Java 对照：** 与 Java IDE 的断点和 Step Over 思路类似；编辑器解释器配置仍需单独检查。

**易错点：** 普通“运行”不一定进入调试，程序太快退出不代表断点机制坏了。

关联：[阶段 01：编辑器与断点](../lessons/01-environment/README.md)。

## K008：Git 与忽略文件

**定义：** 工作区保存当前文件；暂存区选择下一次提交的内容；提交保存版本快照。本地提交不等于推送到远程。

**操作：** `git init` 初始化；`git status` 查看；`git add README.md` 暂存指定文件；`git diff --cached` 查看暂存差异。

**规则：** `.venv/`、缓存和真实密钥不纳入版本管理。本项目已有 `.gitignore`和Git仓库，无需重复初始化；本次教学维护不自动提交。

**易错点：** `.gitignore` 不会让已经跟踪的文件自动停止跟踪。未来配置凭证前，需要确认未进入版本管理。

关联：[阶段 01：Git 入门](../lessons/01-environment/README.md)。

## 从讲义学习，从问题复习

首次学习打开各阶段README，从场景、小例子和执行过程建立理解；课后的knowledge用于回忆与检查，不要求先背术语。阶段02已改为“单张工单字典→工单列表→条件与循环→共享引用”的顺序，见[新版讲义](../lessons/02-basic-syntax/README.md)和[复习问题](../lessons/02-basic-syntax/knowledge.md)。

本轮解释修订包括：整数与字符串是不可变对象（不是“通常不可变”）；赋值先求右值再绑定名字；浅复制只新建外层容器；元组不可变不保证内部列表不可变；and在本课比较表达式中得到布尔结果，但一般返回操作数。阶段02还解释get与写入、print与return的差别，使练习骨架不再越过前置语法。对应示例为[工单筛选](../lessons/02-basic-syntax/examples/demo.py)，逐个短片段在讲义中给出。

全课程讲义按“问题→例子→执行推导→反例→独立迁移”组织，复习材料按具体问题重写。教学依据和维护标准见[教学方式](teaching-guide.md)。资料修改是材料维护，不代表学员已经掌握。

## 全部阶段知识索引

下面是可复习的逐课知识，每课链接到详细讲义、代码和参考资料。材料已交付不等于能力已通过。

## 本次新增与修订概念

- **连续项目里程碑与增量契约**：课程小练习检验局部能力，项目关卡要求沿用旧成果并验收接口演进；见[阶段与项目路线](roadmap.md)、[里程碑交付](milestones.md)。
- **机制验收与集成验收**：离线模拟证明确定控制逻辑，真实服务证据证明目标环境接通；待集成不阻塞无依赖学习，也不能记为完整通过；见[集成关卡映射](integrations.md)。
- **单Agent反馈循环**：`history -> model -> action -> tool -> observation -> history`。函数可作为参数注入，工具结果决定下一轮动作；关联阶段13讲义和[feedback_loop.py](../lessons/13-agent-loop/examples/feedback_loop.py)。
- **阶段05分层语法**：普通类/组合、类型标注/dataclass、推导和解包、生成器、装饰器阅读；关联[短示例](../lessons/05-types-objects/examples/01_class_composition.py)至`05_decorators.py`。
- **阶段06分层异步**：同步测试、`await`、信号量并发、超时取消、异步测试；关联[短示例](../lessons/06-async-testing/examples/01_sync_test.py)至`05_async_test.py`。
- **毕业验收矩阵与阈值证据**：覆盖成功、无证据、越权、审批变更、重放冲突、重启、故障定位、发布回滚和新需求；阈值须按场景预先制定并用真实证据报告；见[里程碑5](milestones.md#里程碑-5治理与毕业交付)。

| 阶段 | 知识文档 | 对应讲义 |
| --- | --- | --- |
| 01 | [开发环境与第一个企业助手程序](../lessons/01-environment/README.md) | [讲义](../lessons/01-environment/README.md) |
| 02 | [变量、容器与可变性](../lessons/02-basic-syntax/knowledge.md) | [讲义](../lessons/02-basic-syntax/README.md) |
| 03 | [函数、作用域与模块](../lessons/03-functions-modules/knowledge.md) | [讲义](../lessons/03-functions-modules/README.md) |
| 04 | [文件、JSON与异常边界](../lessons/04-files-errors/knowledge.md) | [讲义](../lessons/04-files-errors/README.md) |
| 05 | [类型、对象与SDK常见语法](../lessons/05-types-objects/knowledge.md) | [讲义](../lessons/05-types-objects/README.md) |
| 06 | [异步、超时、取消与测试](../lessons/06-async-testing/knowledge.md) | [讲义](../lessons/06-async-testing/README.md) |
| 07 | [需求边界与可验收目标](../lessons/07-requirements/knowledge.md) | [讲义](../lessons/07-requirements/README.md) |
| 08 | [模型API、上下文与成本](../lessons/08-model-api/knowledge.md) | [讲义](../lessons/08-model-api/README.md) |
| 09 | [提示词结构、版本与评估](../lessons/09-prompt-engineering/knowledge.md) | [讲义](../lessons/09-prompt-engineering/README.md) |
| 10 | [结构化输出、SSE与取消](../lessons/10-structured-streaming/knowledge.md) | [讲义](../lessons/10-structured-streaming/README.md) |
| 11 | [工具契约与参数校验](../lessons/11-tool-contracts/knowledge.md) | [讲义](../lessons/11-tool-contracts/README.md) |
| 12 | [重试、幂等与不确定结果](../lessons/12-tool-reliability/knowledge.md) | [讲义](../lessons/12-tool-reliability/README.md) |
| 13 | [手写模型—工具循环](../lessons/13-agent-loop/knowledge.md) | [讲义](../lessons/13-agent-loop/README.md) |
| 14 | [消息、事件与最小Runtime](../lessons/14-agent-runtime/knowledge.md) | [讲义](../lessons/14-agent-runtime/README.md) |
| 15 | [工作流、依赖与有限重规划](../lessons/15-workflow-planning/knowledge.md) | [讲义](../lessons/15-workflow-planning/README.md) |
| 16 | [澄清、审批与结果检查](../lessons/16-human-review/knowledge.md) | [讲义](../lessons/16-human-review/README.md) |
| 17 | [文档导入与质量检查](../lessons/17-document-ingestion/knowledge.md) | [讲义](../lessons/17-document-ingestion/README.md) |
| 18 | [带引用的基础RAG](../lessons/18-basic-rag/knowledge.md) | [讲义](../lessons/18-basic-rag/README.md) |
| 19 | [检索优化与定位失败](../lessons/19-retrieval-optimization/knowledge.md) | [讲义](../lessons/19-retrieval-optimization/README.md) |
| 20 | [知识生命周期](../lessons/20-knowledge-lifecycle/knowledge.md) | [讲义](../lessons/20-knowledge-lifecycle/README.md) |
| 21 | [知识权限与冲突](../lessons/21-knowledge-permissions/knowledge.md) | [讲义](../lessons/21-knowledge-permissions/README.md) |
| 22 | [受预算控制的Agentic RAG](../lessons/22-agentic-rag/knowledge.md) | [讲义](../lessons/22-agentic-rag/README.md) |
| 23 | [上下文工程](../lessons/23-context-engineering/knowledge.md) | [讲义](../lessons/23-context-engineering/README.md) |
| 24 | [长期记忆的来源与修正](../lessons/24-long-term-memory/knowledge.md) | [讲义](../lessons/24-long-term-memory/README.md) |
| 25 | [工作空间与任务恢复](../lessons/25-workspace-tasks/knowledge.md) | [讲义](../lessons/25-workspace-tasks/README.md) |
| 26 | [按需加载的能力包](../lessons/26-skills/knowledge.md) | [讲义](../lessons/26-skills/README.md) |
| 27 | [LangGraph状态与中断](../lessons/27-langgraph/knowledge.md) | [讲义](../lessons/27-langgraph/README.md) |
| 28 | [本地MCP接入](../lessons/28-mcp-local/knowledge.md) | [讲义](../lessons/28-mcp-local/README.md) |
| 29 | [远程MCP与故障边界](../lessons/29-mcp-remote/knowledge.md) | [讲义](../lessons/29-mcp-remote/README.md) |
| 30 | [职责划分与路由](../lessons/30-routing-roles/knowledge.md) | [讲义](../lessons/30-routing-roles/README.md) |
| 31 | [主控与子Agent委派](../lessons/31-supervisor-workers/knowledge.md) | [讲义](../lessons/31-supervisor-workers/README.md) |
| 32 | [Handoff控制权交接](../lessons/32-handoff/knowledge.md) | [讲义](../lessons/32-handoff/README.md) |
| 33 | [并行任务与依赖](../lessons/33-parallel-dependencies/knowledge.md) | [讲义](../lessons/33-parallel-dependencies/README.md) |
| 34 | [通信契约与共享状态](../lessons/34-contracts-state/knowledge.md) | [讲义](../lessons/34-contracts-state/README.md) |
| 35 | [生成检查与证据冲突](../lessons/35-review-conflicts/knowledge.md) | [讲义](../lessons/35-review-conflicts/README.md) |
| 36 | [协作失败与总预算](../lessons/36-failure-budgets/knowledge.md) | [讲义](../lessons/36-failure-budgets/README.md) |
| 37 | [跨服务Agent与A2A](../lessons/37-a2a-remote/knowledge.md) | [讲义](../lessons/37-a2a-remote/README.md) |
| 38 | [架构评估与选择](../lessons/38-architecture-evaluation/knowledge.md) | [讲义](../lessons/38-architecture-evaluation/README.md) |
| 39 | [FastAPI服务与事件接口](../lessons/39-fastapi-service/knowledge.md) | [讲义](../lessons/39-fastapi-service/README.md) |
| 40 | [Spring Boot契约与身份](../lessons/40-java-integration/knowledge.md) | [讲义](../lessons/40-java-integration/README.md) |
| 41 | [持久化、事务与恢复](../lessons/41-persistence/knowledge.md) | [讲义](../lessons/41-persistence/README.md) |
| 42 | [Worker队列与租约](../lessons/42-workers-queues/knowledge.md) | [讲义](../lessons/42-workers-queues/README.md) |
| 43 | [审批、幂等与查证](../lessons/43-approval-idempotency/knowledge.md) | [讲义](../lessons/43-approval-idempotency/README.md) |
| 44 | [评估数据与质量标准](../lessons/44-evaluation-data/knowledge.md) | [讲义](../lessons/44-evaluation-data/README.md) |
| 45 | [执行过程与回归测试](../lessons/45-trajectory-tests/knowledge.md) | [讲义](../lessons/45-trajectory-tests/README.md) |
| 46 | [链路追踪、成本与脱敏](../lessons/46-observability/knowledge.md) | [讲义](../lessons/46-observability/README.md) |
| 47 | [提示注入、工具边界与沙箱](../lessons/47-injection-sandbox/knowledge.md) | [讲义](../lessons/47-injection-sandbox/README.md) |
| 48 | [身份、最小权限与多租户隔离](../lessons/48-identity-tenancy/knowledge.md) | [讲义](../lessons/48-identity-tenancy/README.md) |
| 49 | [部署、配置与健康检查](../lessons/49-deployment/knowledge.md) | [讲义](../lessons/49-deployment/README.md) |
| 50 | [版本、发布门槛与回滚](../lessons/50-version-release/knowledge.md) | [讲义](../lessons/50-version-release/README.md) |
| 51 | [性能、成本与容量治理](../lessons/51-capacity-cost/knowledge.md) | [讲义](../lessons/51-capacity-cost/README.md) |
| 52 | [备份恢复、事故与反馈闭环](../lessons/52-operations-recovery/knowledge.md) | [讲义](../lessons/52-operations-recovery/README.md) |
| 53 | [多 Agent 调研助手项目](../lessons/53-research-project/knowledge.md) | [讲义](../lessons/53-research-project/README.md) |
| 54 | [受控编码与数据分析助手项目](../lessons/54-coding-data-project/knowledge.md) | [讲义](../lessons/54-coding-data-project/README.md) |
| 55 | [浏览器与多模态助手项目](../lessons/55-browser-multimodal/knowledge.md) | [讲义](../lessons/55-browser-multimodal/README.md) |
| 56 | [企业知识与工单协作助手：毕业交付](../lessons/56-capstone/knowledge.md) | [讲义](../lessons/56-capstone/README.md) |

练习校验的数据位置：`docs/progress.md`供人阅读，`.local/exercise-progress.json`保存程序需要的持久状态，首次运行校验时生成。后者不是可随意清理的缓存；例如阶段01通过后应保留该文件以供后续重验。参见[自动校验说明](exercise-checks.md)。

### 开放题的自动校验边界（阶段01）

自然表达可以有多种正确写法，例如“未做任何接入”可以描述当前能力，不必出现“能力”二字。自动检查应验证客观结构与行为，不能把标签匹配当成语义理解。见[阶段01启动卡片](../lessons/01-environment/README.md)与[校验说明](exercise-checks.md)。

### 开放表达与接口契约（阶段02、09、13、17、18、23、35、41、53）

自然语言解释可以自由表达，程序间约定的状态码和字段则需稳定。例如阶段13可以回答“工单已关闭”，以trace中的status判断分支；阶段09的分类标签仍需使用约定值。阶段23的source可以独立存储，避免把某一种文本包装当成唯一实现。详见[统一校验说明](exercise-checks.md)及对应课程练习页。
