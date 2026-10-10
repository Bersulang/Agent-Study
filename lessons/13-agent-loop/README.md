# 阶段 13：手写模型—工具循环

## 使用场景

用户问“查询T1并解释状态”。模型可先请求查询，收到观察后结束回答。执行器控制工具和停止条件，不能把模型提议直接当成执行授权。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能追踪一次工具请求如何成为下一轮模型可见的观察，并说明`call_id`怎样关联请求与结果。
- 能区分动作列表回放与反馈循环，并指出模拟模型不能证明什么。
- 能预测预算耗尽、未知工具、业务拒绝和程序错误各自的结束方式。

## 前置知识与阅读顺序

先完成阶段 12 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

动作列表版把未来动作预先写好；只有反馈版才会把工具观察交回决策函数。看`examples/feedback_loop.py`中的调用：

```python
action = model(history)                 # 读取当前历史，选择下一步
value = tools[action.name](**action.arguments)
history.append({"role": "tool", "name": action.name,
                "call_id": step_number, "content": {"ok": True, "value": value}})
```

这里`model`是函数参数：调用者可以换成另一个决策函数，不必改循环。`history`是列表；`append`会改变同一个列表，所以第二次调用看到刚追加的工具结果。工具结果不是“模型猜测”，是本地工具实际返回的数据。

<details><summary>先预测：若`lookup_ticket`返回`status="closed"`，第二次决策会查负责人吗？</summary>

不会。`demo_model`先看最近工具消息；只有工单查询结果为open时才调用`lookup_owner`。若返回open，轨迹是`lookup_ticket → lookup_owner → final`；closed则是`lookup_ticket → final`。

</details>

反例：把`history.append(tool_message)`删掉，模型下一轮只能看到最初用户消息，便会重复查工单或无法解释为什么结束。即使循环正常结束，固定的`demo_model`也只证明控制器传回了观察，不证明真实模型会选对工具。

动作列表版的`max_steps`按动作索引计数；反馈版按模型决策轮数计数。二者同名的停止标签不完全相同，详见文末标签表。

## 演示命令与实际输出

先运行动作列表示例，它让你先观察步数预算与停止原因：

```powershell
python lessons/13-agent-loop/examples/demo.py
```

再运行新增的[反馈循环示例](examples/feedback_loop.py)：

```powershell
python lessons/13-agent-loop/examples/feedback_loop.py
```

`run_agent`每轮把完整`history`交给`model(history)`函数参数；模型根据消息返回`Action`。执行器先追加assistant工具调用记录，再执行工具并追加`role=tool`观测，下一轮模型能读取这个新观测。`call_id`关联同一轮调用和结果。
`demo_model`收到开放工单观测后选择只读`lookup_owner`，收到负责人信息后回答；若工单已关闭，则直接结束。改变工具返回的状态会改变下一步动作。
预算按“模型决策轮数”计数；未知工具、非法动作、工具声明的`ValueError`作为受控失败观测返给模型，达到连续失败上限停止。其他编程错误继续抛出，避免被误当成业务失败；执行前拒绝bool、浮点数等非整数预算。
本例工具都是离线只读夹具，没有实际审批或写操作。写工具需要先学习阶段12/16的服务端权限、幂等与审批机制。

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/13-agent-loop/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
{'reason': 'completed', 'answer': '[脚本模型]T1仍在处理中', 'observations': [{'ok': True, 'data': {'id': 'T1', 'status': 'open'}}]}
{'reason': 'consecutive_failures', 'observations': [{'ok': False, 'error': '未知工具'}, {'ok': False, 'error': '未知工具'}]}
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

两种示例都只验证控制循环如何管理消息和工具，不证明模型能选对动作。此反馈示例使用确定性模拟模型，不证明真实模型质量。

## 演示源码

下面代码摘录用于讲解第一节“动作列表执行器”，不是独立运行文件；请从项目根目录运行上方`demo.py`命令。它不会根据工具观察重新调用模型。第二节反馈闭环的完整实现单独在[feedback_loop.py](examples/feedback_loop.py)，不要把动作列表当成真实反馈循环。

```python
"""脚本模型模拟Agent循环；只验证执行机制。"""
def lookup(arguments):
    if not isinstance(arguments, dict) or set(arguments) != {"id"}:
        raise ValueError("查询需要且只接受id")
    if arguments["id"] != "T1":
        raise ValueError("工单不存在")
    return {"id": "T1", "status": "open"}

TOOLS = {"lookup": lookup}

def run(actions, max_steps=4):
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("步数必须为正整数")
    observations = []
    failures = 0
    for step, action in enumerate(actions):
        if step >= max_steps:
            return {"reason": "step_budget", "observations": observations}
        if not isinstance(action, dict):
            return {"reason": "invalid_action", "observations": observations}
        if action.get("type") == "final":
            text = action.get("text")
            if not isinstance(text, str) or not text.strip():
                return {"reason": "invalid_action", "observations": observations}
            return {"reason": "completed", "answer": text, "observations": observations}
        if action.get("type") != "tool":
            return {"reason": "invalid_action", "observations": observations}
        name = action.get("name")
        tool = TOOLS.get(name) if isinstance(name, str) else None
        try:
            if tool is None:
                raise ValueError("未知工具")
            data = tool(action.get("args"))
            observations.append({"ok": True, "data": data})
            failures = 0
        except ValueError as error:
            observations.append({"ok": False, "error": str(error)})
            failures += 1
        if failures >= 2:
            return {"reason": "consecutive_failures", "observations": observations}
    return {"reason": "model_exhausted", "observations": observations}

if __name__ == "__main__":
    actions = [{"type": "tool", "name": "lookup", "args": {"id": "T1"}},
               {"type": "final", "text": "[脚本模型]T1仍在处理中"}]
    print(run(actions))
    print(run([{"type": "tool", "name": "exec", "args": {}}] * 3))
```

## 代码执行过程与逐段解释

1. run初始化独立观察与失败计数；enumerate同时取得索引与动作。
2. 预算在执行动作前检查；未知或非法动作不会动态执行。
3. tool结果记录为观察，成功把连续失败计数归零。
4. ValueError是预期业务失败；未捕获的程序错误应暴露修复，不能伪造观察成功。
5. 第二次连续失败终止；final返回completed，脚本耗尽但无final返回model_exhausted。

逐轮跟踪`history`：第1轮只有user消息；工具调用后新增assistant调用记录与tool观察；第2轮模型据最近观察决定后续动作。若工具抛出声明的`ValueError`，它会成为受控失败观察；拼写错误等未预期程序错误继续冒泡，便于定位。

## Java 对照

可把`model`看作Java策略接口的实现，把`tools`看作受控的函数注册表。Python把函数本身作为参数传递很直接；Java通常用函数式接口或对象实现相同替换点。两者都需要执行器校验输入，类型声明不能替代运行时检查。

## 易错点与排查

- 工具返回后立即结束：多步任务还需要下一次决策。
- 任何字符串当final：校验非空文本，但事实正确仍要证据评估。
- 无限while True：必须步数、失败与费用预算。
- 把模拟动作当真实智能：脚本动作仅测试循环机制。

遇到重复动作，先检查工具观察是否被追加；遇到错误被误报为成功，检查异常转换范围；遇到超预算，再数模型决策轮数而非成功工具数。

## 独立练习

本课练习分两节，均需完成：

1. **动作列表执行器**：实现`solve(data)`，支持只读search和final，最多3步，未知工具直接停止；返回trace与reason。search接收query且不得空白；final不能为空。解释一步是否包含最终回答。
2. **反馈循环迁移**：设计接收消息历史的模型替身，让工具观测决定后续动作。开放工单要执行后续只读查询，关闭工单直接结束；完成未知工具/拒绝与预算停止案例。

动作列表练习使用[原骨架](exercises/practice.py)，反馈迁移使用[独立骨架](exercises/feedback_practice.py)；细节见[练习说明](exercises/README.md)。两个文件都只提供TODO，不预写循环答案。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/13-agent-loop/exercises/practice.py
python lessons/13-agent-loop/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

## 企业工程延伸

真实模型适配需处理工具call_id、并行调用、拒答和结构化参数。把执行轨迹与最终答案分别评估；“回答对”不能抵消越权或错误副作用。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://developers.openai.com/api/docs/guides/function-calling)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/13-agent-loop/tests -v`。本课手写控制机制，不依赖Agent框架。

## 循环停止标签

下表仅描述较早的动作列表演示`examples/demo.py`：

| reason | 含义 |
| --- | --- |
| completed | 收到合法非空最终文本 |
| step_budget | 下一动作将超步数预算 |
| consecutive_failures | 连续两次预期工具失败 |
| model_exhausted | 替身动作耗尽，未得到最终文本 |
| invalid_action | 动作形状或最终文本不合法 |

`enumerate(actions)`产生从0开始的索引；预算在索引>=max_steps时触发。
本课只验证轨迹机制，脚本final即使与观察冲突也可能过形状校验，质量检查在16与评估阶段。

反馈循环示例`examples/feedback_loop.py`使用`completed`、`step_budget`、`consecutive_failures`三种结束原因。它不使用`model_exhausted`或`invalid_action`作为最终reason；非法动作会成为失败观测，在达到连续失败上限时结束。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 13`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
