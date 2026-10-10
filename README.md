# 从 Python 复习到企业级 Agent 开发

这是一套围绕项目推进的学习材料。Python 从基础重讲，结合 Java Web 经验；最终学习目标是独立开发、验证、部署和维护企业 Agent。

## 从这里开始

练习完成后运行`.\.venv\Scripts\python.exe tools/check_exercise.py 01`（把01换成当前阶段）。检查你的代码并自动更新练习进度，无需手填运行输出；操作说明见[练习自动校验](docs/exercise-checks.md)。

全部 **56 个阶段**的讲义、知识说明、演示、独立练习、参考答案与验收标准已交付。当前学习仍从 **[阶段 01：开发环境与第一个企业助手程序](lessons/01-environment/README.md)** 开始。

先阅读课程，再运行示例，最后独立完成练习。阶段 01 不需要 API Key，不调用模型，不安装第三方依赖。

在 PowerShell 中，进入项目根目录：

```powershell
cd C:\Users\Mason\Desktop\agent-study
```

创建项目虚拟环境（这条命令通常只需执行一次）：

```powershell
python -m venv .venv
```

运行第一个示例：

```powershell
.\.venv\Scripts\python.exe .\lessons\01-environment\examples\hello_agent.py
```

预期输出：

```text
企业知识与工单助手
当前版本：只展示启动信息
下一步：学习如何接收和处理工单
```

这是未来 Agent 项目的起点，当前尚未具备模型、工具和自主执行能力。各条命令的含义在阶段 01 中逐项讲解。

## 讲义怎样读

首次学习先读每课README，跟着一个具体问题走：读小例子、预测结果、核对执行过程，再完成独立练习。课内knowledge是复习问答，不用先背完整名词表。[阶段02](lessons/02-basic-syntax/README.md)从单张工单的数据表示逐步讲到循环与共享引用，可作为这种学习方式的示例。教学结构说明见[教学方式](docs/teaching-guide.md)。

## 学习导航

| 文档 | 用途 |
| --- | --- |
| [完整进阶路线与课程目录](docs/roadmap.md) | 12 个模块、56 个能力阶段；每阶段可直接打开 |
| [连续项目里程碑](docs/milestones.md) | 把阶段成果接成五个可运行、可验收的主项目增量 |
| [知识文档](docs/knowledge.md) | 持续维护的概念、Java 对照、命令和易错点 |
| [学习进度](docs/progress.md) | 分开记录材料状态、练习状态和能力验收 |
| [教学方式](docs/teaching-guide.md) | 每课怎样讲、练、检查和维护注释 |
| [全课程验证报告](docs/verification-report.md) | 实际测试结果、真实集成与未验证环境 |
| [集成环境说明](docs/integrations.md) | 模型、框架、协议、服务、浏览器与部署的安装入口 |
| [维护指南](CONTRIBUTING.md) | 修改课程、补知识、执行回归和维护Git |

## 完整交付内容

- 阶段 01：环境运行、逐步操作、独立启动卡片与自动代码校验。
- 阶段 02—56：逐课讲义、知识、注释演示、练习要求与骨架、参考答案和验收。
- Python、模型调用、工具与单Agent、RAG、记忆、Skills、框架、MCP、完整多Agent、A2A、后端、审批恢复、评估安全、生产治理、专项与毕业项目。
- 实际模型HTTP、pypdf、LangGraph、MCP、A2A、FastAPI、Spring Boot、OpenTelemetry、Playwright、图像/音频与Docker接入文件。
- 本地验证脚本与行为回归。

默认示例无模型密钥、无网络依赖。模拟模型、教学向量、内存队列和协议子集均标注边界；真实SDK和外部环境的验证范围见报告。

默认代码由助手验证可运行，**你的学习能力仍待验收**。完成阶段01练习后运行自动校验，结果直接更新进度，无需填写提交表；概念疑问可在对话中继续讲解和验收。后续每课使用相同入口和对应编号。

## 验证与维护

从项目根目录执行：

```powershell
.\.venv\Scripts\python.exe tools/verify_course.py
```

也可使用干净环境的Python 3.12执行 `python tools/verify_course.py`。它检查56阶段材料、所有课程源码语法、本地链接、默认演示、练习骨架、参考答案和标准库测试；报告写入忽略目录 `artifacts/verification-report.json`。

真实集成按各课 `integrations/README.md` 安装、验证，不被默认检查暗中调用。部分SDK需独立环境，以防不同阶段的版本要求互相影响。

## 项目结构

```text
agent-study/
├── README.md                       # 学习入口
├── AGENTS.md                       # 后续教学与维护约定
├── docs/
│   ├── roadmap.md                  # 全部 56 个阶段
│   ├── milestones.md               # 同一主项目的五个集成里程碑
│   ├── knowledge.md                # 累积知识手册
│   ├── progress.md                 # 学习与交付状态
│   ├── teaching-guide.md           # 教学方式
│   ├── integrations.md             # 真实集成环境和命令入口
│   └── verification-report.md      # 全课程验证与边界
├── lessons/
│   ├── 01-environment/
│   │   ├── README.md               # 本阶段讲义
│   │   ├── examples/               # 跟着运行的演示
│   │   ├── exercises/              # 你独立完成的练习
│   │   └── solutions/             # 做完练习后查看的答案
│   └── 02-... 至 56-capstone/       # 全部进阶课程与集成
├── tools/verify_course.py          # 统一验证入口
├── tests/                          # 验证器自身回归
├── course.json                     # 机器可读课程目录
└── .venv/                          # 本地环境，不纳入版本管理
```

## 环境基线

本次在 Windows PowerShell、Python 3.12.10 下验证。默认课程使用标准库；可选SDK版本与真实检查记录见 [验证报告](docs/verification-report.md)。

所有命令默认从项目根目录执行。未激活虚拟环境也可以按上面的完整路径运行。遇到问题先保存命令与完整错误信息，按讲义排查；不要贴出密钥或私人业务数据。

## Git初始化

本项目使用本地 `main` 分支，按用户指定作者记录初始化提交，提交描述为“初始化工程”。未配置或推送远程仓库；后续在你自己的仓库设置remote并维护。
