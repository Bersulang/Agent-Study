# 阶段 13：手写模型—工具循环

## 使用场景

用户问“查询T1并解释状态”。模型可先请求查询，收到观察后结束回答。执行器控制工具和停止条件，不能把模型提议直接当成执行授权。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 12 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. 动作与观察

动作是模型提出的下一步，观察是工具真实执行结果。

用途与例子：lookup(T1)产生open观察；最终回答必须引用观察，不能提前假定结果。

### 2. ReAct与控制循环

ReAct结合推理与行动；工程循环是请求决策、执行允许工具、回传观察、判断终止。

用途与例子：教学脚本只模拟动作序列，不展示或要求保存模型隐藏思维链。

### 3. 停止条件

循环必须有最终响应、步数预算、连续失败、取消等终止原因。

用途与例子：两次未知工具错误转停止；max_steps包括最终决策，边界需要明确。

### 4. 模型替身与质量边界

确定性替身用于验证控制流，不证明真实模型会选对工具。

用途与例子：本课actions列表预写动作；真实接入时用08适配器加供应商工具调用响应转换。

## 演示命令与实际输出

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

## 演示源码

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

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

类似Java解释器或状态机驱动器，而不是无限while聊天。函数注册表对应受控策略列表；每轮观察应附call_id，真实工具响应需与请求正确关联。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 工具返回后立即结束：多步任务还需要下一次决策。
- 任何字符串当final：校验非空文本，但事实正确仍要证据评估。
- 无限while True：必须步数、失败与费用预算。
- 把模拟动作当真实智能：脚本动作仅测试循环机制。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data为动作列表，支持只读search和final，最多3步，未知工具直接停止；返回trace与reason。search接收query且不得空白；final不能为空。解释一步是否包含最终回答。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
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
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

真实模型适配需处理工具call_id、并行调用、拒答和结构化参数。把执行轨迹与最终答案分别评估；“回答对”不能抵消越权或错误副作用。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://developers.openai.com/api/docs/guides/function-calling)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/13-agent-loop/tests -v`。本课手写控制机制，不依赖Agent框架。

## 循环停止标签

| reason | 含义 |
| --- | --- |
| completed | 收到合法非空最终文本 |
| step_budget | 下一动作将超步数预算 |
| consecutive_failures | 连续两次预期工具失败 |
| model_exhausted | 替身动作耗尽，未得到最终文本 |
| invalid_action | 动作形状或最终文本不合法 |

`enumerate(actions)`产生从0开始的索引；预算在索引>=max_steps时触发。
本课只验证轨迹机制，脚本final即使与观察冲突也可能过形状校验，质量检查在16与评估阶段。
