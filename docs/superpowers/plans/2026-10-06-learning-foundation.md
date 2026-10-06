# Agent 学习基础 Implementation Plan

> **For agentic workers:** 执行方式为当前会话原地实施；本批为文档与低影响教学示例，不使用子 Agent。步骤使用复选框追踪。

**Goal:** 交付课程导航、知识文档和可直接学习的第一阶段。

**Architecture:** Markdown 保存教学内容；每阶段独立组织示例、练习和答案。标准库脚本仅演示输出和运行环境。

**Tech Stack:** Python 3.12、Windows PowerShell、Markdown。

**Spec:** [内容设计](../specs/2026-10-06-learning-foundation-design.md)

## Global Constraints

- Windows PowerShell；基线 Python 3.12；本阶段仅使用标准库。
- 虚拟环境直接指定解释器运行，激活作为可选知识。
- 代码运行验证不等于学员通过验收。
- 用户指定的空目录原地实施；不提交、不推送。

## Review Focus

- PowerShell 激活被策略阻止时仍能运行课程。
- 中文路径与中文输出能正常工作。
- 从项目根目录执行所有文档命令。
- 练习不能默认包含完整参考答案。
- 资料交付状态和学员掌握状态明确区分。

## Task 1：课程导航与维护机制

Files: `README.md`, `AGENTS.md`, `.gitignore`, `docs/roadmap.md`, `docs/teaching-guide.md`, `docs/knowledge.md`, `docs/progress.md`。

Produces: 上述文件为课程固定入口；知识条目按概念编号，进度按阶段编号。

- [x] 写入路线、教学规则、知识和进度。
- [x] 检查阶段编号 01—56 完整且唯一。
- [x] 检查文档链接目标存在。

## Task 2：第一阶段讲义与练习

Files: `lessons/01-environment/README.md`, `examples/hello_agent.py`, `examples/environment_info.py`, `exercises/startup_card.py`, `exercises/submission.md`, `solutions/startup_card.py`（后五个路径均位于阶段目录）。

Consumes: Task 1 的课程入口和知识文档。

Produces: 学员可从 README 进入阶段 01，运行示例、完成练习并提交验收。

- [x] 写场景、知识、命令、预期结果、逐行解释和错误排查。
- [x] 写不涉及模型调用的演示和练习。
- [x] 创建 `.venv`，运行所有脚本，检查语法。
- [x] 核对文档中的运行命令与真实输出；编辑器和 Git 操作明确为学员练习。

## Task 3：交付检查与进度更新

- [x] 检查全部相对链接和 56 个路线阶段。
- [x] 记录实际环境版本和验证结果。
- [x] 将阶段 01 标为材料已准备、能力待验收。
- [x] 给出直接入口与下一项学习任务，写入项目 README。

## 完成记录

2026-10-06：10 份 Markdown、4 个中文注释教学脚本与 `.gitignore` 已交付。虚拟环境和脚本实跑通过，本地链接及路线编号检查通过。无第三方依赖安装、模型调用、Git 提交或推送。阶段 02—56 尚未制作详细讲义。
