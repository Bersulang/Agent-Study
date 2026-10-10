# 阶段 15：工作流、依赖与有限重规划

## 使用场景

制度查询通常走固定流程：识别意图、检索、检查证据、回答。没有证据时允许把“回答”改成“转人工”，但不允许无限重新规划。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能解释`state`、待执行`plan`与已发生`history`为什么分开保存。
- 能用依赖集合阻止未检索就回答，并追踪缺证据后的单次重规划。
- 能预测未识别问题、无重规划预算和证据命中时的不同终态。

## 前置知识与阅读顺序

先完成阶段 14 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

演示把流程中的三个问题分开回答：`state`现在到哪了，`plan`接下来做什么，`history`已经发生了什么。初始计划是`search → answer`，依赖表要求answer必须先有search：

```python
if not DEPENDENCIES[step] <= set(state["completed"]):
    raise ValueError("步骤依赖未满足")
```

`<=`表示左侧集合是右侧的子集。search不需要先完成任何步骤；answer要求`search`已完成。即使计划器把answer放到最前面，执行器也会在动作发生前拒绝。

<details><summary>先预测：`workflow("登录", evidence=False, max_replans=1)`会再搜一次吗？</summary>

不会。第一次search记入completed和history后，程序只把尚未执行的answer替换成human_review，replans变为1。轨迹保留`retrieved`和`replanned`，终态为human_review。若预算为0，则记录stopped；未识别的问题在检索前进入clarify。

</details>

反例：若重规划时清空history，运维和调用者就看不到已做过的搜索；若无限重试search，空资料也可能制造无休止成本。这里的计划是固定分支演示，不是模型自主规划器。

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

正常路径逐步为：输入被路由→取出search→空依赖满足→记录检索→`completed={search}`→answer依赖满足→终态answered。无证据路径在检索之后替换剩余计划，但不回滚已完成步骤。

## Java 对照

Java开发者可以把它看作简化的BPM状态机；`set`依赖检查对应服务层的前置条件验证。Python集合可直接用`<=`表达子集，Java则常用`containsAll`。固定流程比Agent更适合稳定、可预测的审批链路。

## 易错点与排查

- 规划器输出先answer：执行器需拒绝依赖未满足。
- 重规划清空历史：会丢失已发生动作和可能副作用。
- 无证据反复检索：设置预算和转人工条件。
- state与history不一致：本课history包括中间记录，最终state只保存当前终态。

若answer提前报依赖错误，检查completed更新位置；若无证据仍回答，检查search后的分支是否替换了剩余计划；若轨迹丢步骤，检查是否误把history当成当前state覆盖。

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
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 15`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
