# 阶段 07：需求边界与可验收目标

## 使用场景

业务方说“做一个聪明助手”，工程师需要把它转成明确任务：查询工单、回答制度、生成草稿，以及禁止未审批写入。先设计可观察行为，再决定是否需要Agent。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

从本课起建立固定小型评估集：将开发调试样例与保留验收样例分开，记录输入、可接受结果和失败边界。后续扩展沿用[主项目里程碑](../../docs/milestones.md)，不要只保存“成功答案”。

- 能把自然语言请求映射成澄清、拒绝、只读、待审批或转人工等明确决策。
- 能为每个分支写出输入、期望决策和禁止行为，并解释缺权限为何默认拒绝。
- 能追踪评估集的实际值与预期值，说明规则模拟的证据边界。

## 前置知识与阅读顺序

先完成阶段 06 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 聊天、工作流与Agent

客户说“帮我处理工单”时，先问工程上到底要得到什么。若答案只是给出当前状态，就是一次问答；若每次都按“验证身份→查工单→显示状态”执行，就是固定工作流；只有当下一步确实需要依据结果选择（例如缺少证据时再检索或转人工），才需要Agent式决策。本课`decide`是明确的规则函数，故意不引入模型。

决策能力不意味着权限。代码即使由模型给出计划，读取服务仍应核验身份、权限和对象范围；写入则要走单独审批流程。

下面是帮助说明“先校验对象ID，再检查权限”的示意伪代码，并非`demo.py`中的可运行函数：

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
if intent == "lookup_ticket":
    return check_id_then_permission(request)
```

固定次序由工程师规定时，这是工作流；只有下一步需要依据观察选择，才引入动态决策。

Java对照：需求先约束Controller/Service可做的操作，随后才决定是否用规则、状态机或模型。不要因“Agent”听起来先进就跳过固定流程。

<details><summary>先预测：查状态总是依次验证权限再读数据库，是否需要Agent动态选工具？</summary>

不需要。步骤固定时，普通业务工作流更简单、可测。若读取结果可能决定“继续查证据还是转人工”，才有需要研究受限的动态选择。
</details>

### 2. 需求边界

边界不是一段“请安全回答”的提示，而是一份程序可执行的契约：要哪些输入、允许哪些动作、哪些动作禁止、缺少信息时怎么处理。演示里查工单先要`id`，再检查`can_read`；权限字段缺失时默认False，按失败关闭处理。

创建请求只得到`draft_for_review`，不调用写工具。未知意图返回`human_handoff`。这些标签表示程序决策，不是面向客户的最终文案，也不是权限服务本身。

```python
if not request.get("id"):
    return "clarify"
if not request.get("can_read", False):
    return "deny"
```

分支顺序很重要：缺ID时先澄清；补上ID后仍需授权。默认`False`意味着输入遗漏时不会开放读取。

<details><summary>先预测：request只有intent=lookup_ticket、id=T1而没有can_read时，结果是什么？</summary>

`request.get("can_read", False)`返回False，因此是`deny`。默认值不能改成True；否则缺权限信息会被当成允许。
</details>

### 3. 成功标准与评估案例

“体验好”不能直接自动验收；“缺少工单编号要澄清”“未授权读取为deny”“创建请求只生成待审草稿”可以变成输入和预期决策。`evaluate`里的每一项是`(request, expected)`，评估时调用`decide(request)`并比较实际值与预期值，累计正确数。

固定集应包括正常、缺字段、无权限、无依据、冲突和注入文本。只算总体命中率会掩盖一条严重越权；安全失败应单独报告，不能被大量容易的正例平均掉。

```python
cases = [
    ({"intent": "lookup_ticket"}, "clarify"),
    ({"intent": "lookup_ticket", "id": "T1", "can_read": False}, "deny"),
]
```

每个元组把一个输入和期望标签固定在一起，需求就能转成可回归案例。

<details><summary>先预测：给当前四个案例再加100个普通成功案例，是否就能证明没有未授权写入？</summary>

不能。案例覆盖范围决定我们检查了什么；当前4个案例再加100个普通成功案例，即使104/104通过，也没有提供越权路径的证据。保留安全边界案例并逐项分析。
</details>

### 4. 失败分类

缺少参数、权限不足、无证据、模型超时、工具故障分别需要不同处置：澄清、拒绝、转人工或重试/降级。把接口故障返回成“没找到工单”会给用户错误事实；把权限不足当未知问题更可能诱发危险重试。

| 观测到的情况 | 程序决策 | 为什么不能合并 |
| --- | --- | --- |
| 没有ID | clarify | 需要用户补输入 |
| 有ID但无权读取 | deny | 继续尝试会越权 |
| 无制度证据 | human_handoff | 编造答案会误导 |
| 创建请求 | draft_for_review | 尚未获得写审批 |

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/07-requirements/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
预期=clarify 实际=clarify
预期=deny 实际=deny
预期=draft_for_review 实际=draft_for_review
预期=human_handoff 实际=human_handoff
规则案例：4/4；不代表模型质量
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""需求规则演示：没有模型，输出是规则决策。"""
def decide(request):
    intent = request.get("intent")
    if intent == "lookup_ticket":
        if not request.get("id"):
            return "clarify"
        if not request.get("can_read", False):
            return "deny"
        return "read_only"
    if intent == "create_ticket":
        return "draft_for_review"
    return "human_handoff"

def evaluate(cases):
    correct = 0
    for request, expected in cases:
        actual = decide(request)
        correct += actual == expected
        print(f"预期={expected} 实际={actual}")
    return correct, len(cases)

if __name__ == "__main__":
    cases = [
        ({"intent": "lookup_ticket"}, "clarify"),
        ({"intent": "lookup_ticket", "id": "T1", "can_read": False}, "deny"),
        ({"intent": "create_ticket"}, "draft_for_review"),
        ({"intent": "unknown"}, "human_handoff"),
    ]
    correct, total = evaluate(cases)
    print(f"规则案例：{correct}/{total}；不代表模型质量")
```

## 代码执行过程与逐段解释

以第一个评估项`({"intent":"lookup_ticket"}, "clarify")`为例：输入没有id，`not request.get("id")`为真，函数立即返回clarify，不会继续检查权限。第二项带id但`can_read=False`，先通过id分支，再返回deny。第三项create_ticket返回draft_for_review；第四项unknown落到human_handoff。`evaluate`把每次布尔比较加入整数计数，True按1计、False按0计，最后显示4/4。

失败反例：仅增加正例会让覆盖数字变大，却不证明越权路径安全；规则例全通过也不代表真实模型遵循提示，更不代表权限系统正确。

## Java 对照

可类比Java在Controller校验请求、Service执行业务规则、测试固定输入输出。本课把三个层次压缩在纯Python函数中便于观察，但生产Agent也不能让模型跳过身份授权、审批和验收。

## 易错点与排查

- “体验好”无法验收：改成具体输入、决策和证据。
- 把高命中率当安全：单独统计越权和未审批写入。
- 未知意图默认执行：未知应澄清或转人工。
- 只测正常问题：加入缺失id、权限不足、资料冲突与工具故障。

排查顺序：先选一个输入案例并写下expected，再沿`decide`分支确认实际标签；若标签正确但统计错误，检查`evaluate`是否处理了全部case；若安全结论过强，检查评估集是否真的包含该危险路径。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：为批量请求返回决策列表，新增“制度问答”：有证据且can_read为True才answer；缺证据human_handoff；无权限deny。自行写6条固定评估案例。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/07-requirements/exercises/practice.py
python lessons/07-requirements/solutions/solution.py
```

## 能力验收

1. 实现六条固定案例，覆盖制度有证据、无证据、无权限、缺参数与注入文本，并比较预期决策和实际决策。
2. 解释请求如何进入澄清、拒绝、待审批或转人工分支，说明缺权限为何失败关闭。
3. 指出案例没有覆盖的风险；不把规则模拟分数报告成真实模型质量。
4. 用Java的Controller、Service与验收测试说明同一边界，并指出Agent决策不能绕过服务端权限。
5. 自动校验保存代码案例结果；人工验收仍需说明案例选择依据。

## 企业工程延伸

将需求案例存成版本化评估集，每次换模型、提示词或工具契约都回归。不同任务分别设延迟、成本、质量与安全边界；此处不虚构统一企业指标。

本课只写需求到决策标签的规则，不调用模型、数据库或写入服务。后续阶段会分别加入模型、工具、权限与审计；当前评估集应保留为回归基线。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/unittest.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

## 将模糊需求写成验收表

| 输入情形 | 允许决策 | 禁止行为 |
| --- | --- | --- |
| 缺少工单id | clarify | 猜测客户工单 |
| 无读取权限 | deny | 请求模型绕过权限 |
| 制度没有依据 | human_handoff | 编造引用 |
| 请求创建工单 | draft_for_review | 未审批写入 |

案例中 `(request, expected)` 是两个元素的元组；for使用解包分别绑定它们。
业务决策标签是内部契约，展示给用户时应转成清楚中文说明。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 07`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
