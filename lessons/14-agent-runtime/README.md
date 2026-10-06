# 阶段 14：消息、事件与最小Runtime

## 使用场景

循环工作了，但运维不知道卡在哪一步。Runtime把消息、状态、事件、工具和预算集中管理，出现停止或取消时能准确解释原因。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 13 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 消息、状态、事件

消息承载对话内容；状态描述当前执行进度；事件记录已经发生的变化。

用途与例子：messages保存工具结果，used表示已使用预算，tool_started记录开始边界。

### 2. 工具注册与中间件

注册表定义可调用能力；中间件围绕调用实施统一策略。

用途与例子：before_tool先检查取消/预算，再调用工具；真实系统还可加审计与权限。

### 3. 预算与停止原因

预算是执行前的资源上限；停止原因解释为什么任务终止。

用途与例子：budget=1只允许一次工具执行，第二次在调用前停止，不是先执行再计数。

### 4. 取消与生命周期

取消是一种控制信号；开始、运行、停止应有明确状态与事件。

用途与例子：本课在步骤边界检查取消，无法中断正在运行的阻塞工具，异步取消见06。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/14-agent-runtime/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
状态：stopped；停止原因：budget；已用预算：1
事件：['started', 'tool_started', 'tool_completed', 'stopped']
提前取消：cancelled
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""最小同步Runtime；事件与状态只在内存中，不是持久化框架。"""
def lookup():
    return {"id": "T1", "status": "open"}

TOOLS = {"lookup": lookup}

def before_tool(state, cancelled):
    # 中间件只决定能否开始，尚未产生业务副作用。
    if cancelled():
        return "cancelled"
    if state["used"] >= state["budget"]:
        return "budget"
    return None

def execute(names, budget=3, cancelled=lambda: False):
    if type(budget) is not int or budget < 0:
        raise ValueError("预算必须是非负整数")
    state = {"status": "running", "used": 0, "budget": budget,
             "messages": [], "events": [{"type": "started"}], "reason": None}
    for step, name in enumerate(names):
        reason = before_tool(state, cancelled)
        if reason:
            state["reason"] = reason
            break
        tool = TOOLS.get(name) if isinstance(name, str) else None
        if tool is None:
            state["reason"] = "unknown_tool"
            break
        state["used"] += 1
        state["events"].append({"type": "tool_started", "step": step, "name": name})
        try:
            result = tool()
        except Exception as error:
            # Runtime边界转换为明确终止；记录类型而不泄露敏感异常正文。
            state["events"].append({"type": "tool_failed", "step": step, "error_type": type(error).__name__})
            state["reason"] = "tool_error"
            break
        state["messages"].append({"role": "tool", "name": name, "content": result})
        state["events"].append({"type": "tool_completed", "step": step})
    if state["reason"] is None:
        state["reason"] = "completed"
    state["status"] = "stopped"
    state["events"].append({"type": "stopped", "reason": state["reason"]})
    return state

if __name__ == "__main__":
    state = execute(["lookup", "lookup"], budget=1)
    print(f"状态：{state['status']}；停止原因：{state['reason']}；已用预算：{state['used']}")
    print(f"事件：{[event['type'] for event in state['events']]}")
    print(f"提前取消：{execute(['lookup'], cancelled=lambda: True)['reason']}")
```

## 代码执行过程与逐段解释

1. execute构造本次任务独立状态；started表明生命周期开始。
2. before_tool作为统一门禁检查取消和预算，失败时不会调用函数。
3. 查询注册表，未知工具直接设置停止理由；预算不会被未知工具扣减。
4. 已知调用开始时used加一并写tool_started，完成后写消息与tool_completed。
5. 任何路径最后写stopped事件，state里reason解释完成、预算、取消或错误。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

可类比Java拦截器、执行上下文与应用事件，但这里中间件只是普通函数，不需要Spring容器。Python字典状态容易修改，需要明确所有权；真实事件可用不可变对象与序号。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 执行后再检查预算：已经发生未允许的副作用。
- 混淆messages和events：面向模型的消息不等于运维审计。
- 只打印异常继续：应给终止理由与tool_failed事件。
- 同步取消误认为能杀线程：这里只在步骤边界检查，阻塞调用需超时或隔离。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data为工具名列表，每次最多2次lookup，支持cancel_before_step索引（可通过输入字典传入）。返回事件序列、used与reason；取消/预算发生时不能产生对应tool_started。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/14-agent-runtime/exercises/practice.py
python lessons/14-agent-runtime/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

最小Runtime未持久化、无多进程隔离，也不等于生产沙箱。后续增加任务ID、调用ID、费用预算、事件序号、检查点和恢复；预算应区分模型次数、工具次数与真实费用。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/asyncio-task.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/14-agent-runtime/tests -v`。本课设计是教学自编Runtime，官方来源用于核查取消与任务机制，不声称Python官方定义本Runtime结构。

## 预算与事件的设计取舍

本例每次已知工具调用开始就消耗一单位；失败调用也收费于该次数预算。
unknown_tool没有实际执行，不消耗used。预算0也合法，表示禁止工具执行。
在服务边界捕获Exception会转成tool_error停止，区别于业务函数内部吞错继续执行。
消息content这里使用本地字典；发送真实模型时需按供应商格式序列化，不能直接假定API接受。
`lambda: True`表示一个总返回True的函数，用于演示调用前已取消。
