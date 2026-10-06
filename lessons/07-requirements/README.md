# 阶段 07：需求边界与可验收目标

## 使用场景

业务方说“做一个聪明助手”，工程师需要把它转成明确任务：查询工单、回答制度、生成草稿，以及禁止未审批写入。先设计可观察行为，再决定是否需要Agent。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 06 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 聊天、工作流与Agent

聊天以回答为主要产物；工作流由工程师确定步骤；Agent根据观察选择下一步。

用途与例子：查工单固定步骤可用工作流；证据不足时选择再检索才需要受限动态决策。

### 2. 需求边界

边界明确输入、允许动作、禁止动作与转人工条件。

用途与例子：不提供工单id时先澄清；没有权限时拒绝，不能请模型猜id。

### 3. 成功标准与评估案例

成功标准是可判定条件；评估案例固定输入、预期决策与依据。

用途与例子：成功不仅回答对，还要零未授权写入；无依据问题应该转人工。

### 4. 失败分类

区分无法判断、权限不足和接口故障，才能选择合适兜底。

用途与例子：未知意图需要澄清，不应该当成查询工单成功。

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

1. 业务输入作为字典传入；get在缺失时返回默认值。
2. 查工单先检查id，再检查权限；权限缺省为False，失败关闭。
3. 创建意图只能生成待审草稿，不在decide中执行写入。
4. 评估每个固定案例，将实际决策与预期比较。
5. 布尔值参与加法得到正确数；仅覆盖四个规则分支，不证明所有场景。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

可类比Java业务需求中的Controller输入、Service规则和验收测试；Agent也不能跳过这些层。Python规则函数很短，不代表业务边界可以省略。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- “体验好”无法验收：改成具体输入、决策和证据。
- 把高命中率当安全：单独统计越权和未审批写入。
- 未知意图默认执行：未知应澄清或转人工。
- 只测正常问题：加入缺失id、权限不足、资料冲突与工具故障。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
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

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

将需求案例存成版本化评估集，每次换模型、提示词或工具契约都回归。不同任务分别设延迟、成本、质量与安全边界；此处不虚构统一企业指标。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

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
