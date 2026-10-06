# 阶段 15：工作流、依赖与有限重规划

## 使用场景

制度查询通常走固定流程：识别意图、检索、检查证据、回答。没有证据时允许把“回答”改成“转人工”，但不允许无限重新规划。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 14 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 状态机与合法转移

状态机把流程表示为有限状态与允许的转移；非法跳转应拒绝。

用途与例子：received→routed→retrieved→answered；无法识别意图时转clarify。

### 2. 步骤依赖

依赖规定某步需要哪些前置产物；执行器检查，而不是靠模型记住顺序。

用途与例子：answer需要search证据；无证据不能先回答再补引用。

### 3. 规划与重规划

规划决定下一批步骤；重规划根据新观察调整尚未执行部分。

用途与例子：检索无结果把answer替换为human_review，保留已发生的检索记录。

### 4. 有限动态与预算

动态决策受任务、工具白名单和次数约束，始终有终态。

用途与例子：max_replans=0时无证据直接stopped，不重复搜索直至“满意”。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/15-workflow-planning/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
证据=True；终态=answered；轨迹=['received', 'routed', 'retrieved', 'answered']
证据=False；终态=human_review；轨迹=['received', 'routed', 'retrieved', 'replanned', 'human_review']
未知问题终态：clarify
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""固定工作流加一次受限重规划；没有真实模型规划。"""
DEPENDENCIES = {"search": set(), "answer": {"search"}, "human_review": {"search"}}

def workflow(query, evidence=True, max_replans=1):
    if type(max_replans) is not int or max_replans < 0:
        raise ValueError("重规划预算必须为非负整数")
    state = {"state": "received", "history": ["received"], "replans": 0, "completed": []}
    if query not in ("登录", "VPN"):
        state["state"] = "clarify"
        state["history"].append("clarify")
        return state
    state["history"].append("routed")
    plan = ["search", "answer"]
    while plan:
        step = plan.pop(0)
        # 依赖由程序检查，不能信任规划器输出的顺序。
        if not DEPENDENCIES[step] <= set(state["completed"]):
            raise ValueError("步骤依赖未满足")
        if step == "search":
            state["completed"].append("search")
            state["history"].append("retrieved")
            if not evidence:
                if state["replans"] >= max_replans:
                    state["state"] = "stopped"
                    state["history"].append("stopped")
                    return state
                state["replans"] += 1
                # 只替换未执行部分；已经发生的search不重做。
                plan = ["human_review"]
                state["history"].append("replanned")
        elif step == "answer":
            state["state"] = "answered"
            state["history"].append("answered")
        else:
            state["state"] = "human_review"
            state["history"].append("human_review")
    return state

if __name__ == "__main__":
    for evidence in (True, False):
        result = workflow("登录", evidence=evidence)
        print(f"证据={evidence}；终态={result['state']}；轨迹={result['history']}")
    print(f"未知问题终态：{workflow('其他')['state']}")
```

## 代码执行过程与逐段解释

1. 输入未被规则识别时进入clarify并立即返回，不执行search。
2. 已识别问题建立search/answer计划；pop(0)取出下一步。
3. 执行前用集合子集关系检查依赖：所需步骤必须已经完成。
4. search后检查证据；缺证据且有预算则重规划为human_review。
5. history保留retrieved与replanned，最终answered、人审或stopped均有明确终态。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

可类比Java业务状态机或BPM流程，但本课是普通Python数据与分支。工作流不等于Agent；当只有已知路径时，固定流程通常更易测试和维护。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 规划器输出先answer：执行器需拒绝依赖未满足。
- 重规划清空历史：会丢失已发生动作和可能副作用。
- 无证据反复检索：设置预算和转人工条件。
- state与history不一致：本课history包括中间记录，最终state只保存当前终态。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data含query/evidence/allowed，先权限检查，再检索；未授权denied，缺证据human_review，有证据answered；answer依赖search。返回trace，任何失败不得写工单。添加一次query_rewrite只在缺证据时使用，总共最多两次search。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/15-workflow-planning/exercises/practice.py
python lessons/15-workflow-planning/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

后续框架迁移先保存状态与转移契约，再换执行引擎。规划器只能选择允许步骤；含写入的计划需审批、幂等与恢复，计划文字不能作为执行凭据。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/graphlib.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/15-workflow-planning/tests -v`。本课依赖集合是小规模演示；更复杂DAG可用标准库graphlib，但还需业务状态与失败规则。

## 依赖检查的语法

`required <= completed`表示左侧集合是右侧子集；不是比较集合大小。
`set()`是空集合；空依赖集合总是已完成集合的子集。
`plan.pop(0)`移除并返回首元素，适合很短教学计划；大队列可用collections.deque。
状态机记录“现在处于哪里”，计划记录“还要做什么”，history记录“已经发生什么”。
三个结构不能混为一份可随意覆盖的文本计划。
