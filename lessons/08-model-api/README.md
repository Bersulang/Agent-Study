# 阶段 08：模型API、上下文与成本

## 使用场景

从规则系统走向模型问答前，先认识请求消息、响应文本和计费用量，并把模型供应商差异关在适配器中。默认程序使用明确标注的模拟模型；真实HTTP在integrations中单独运行。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 07 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

### 1. Token与上下文窗口

Token是模型处理文本的单位，不等于字符或词；上下文窗口限制一次请求可处理的输入与输出。

用途与例子：中文字符数只能作粗略估算，实际token以供应商usage或官方tokenizer为准。

### 2. 角色与消息

消息包含角色与内容；不同API支持不同角色、内容块和指令层级。

用途与例子：user提交问题；system或developer规则依供应商能力选择，不能认为角色名处处通用。

### 3. 适配器与接口故障

适配器把内部请求转换为供应商格式；HTTP成功与答案正确是两层验证。

用途与例子：401通常凭证问题，429可能限流或额度，200也可能返回拒答、非文本或错误事实。

### 4. 用量与成本

费用取决于实际输入/输出token、模型费率和缓存等计费项目。

用途与例子：本课给定教学费率计算，不展示当前真实价格；生产用版本化价目表。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/08-model-api/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
[模拟回答]请核查制度来源：如何申请VPN？
模拟usage：{'input_tokens': 20, 'output_tokens': 10}
教学费率估算：0.000040
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""模拟模型只用于测试接口形状，不代表真实智能。"""
class MockModel:
    def complete(self, messages):
        # 模拟响应明确标记；usage是固定教学数据，不是tokenizer结果。
        question = messages[-1]["content"]
        return {"text": f"[模拟回答]请核查制度来源：{question}",
                "usage": {"input_tokens": 20, "output_tokens": 10}}

def estimated_cost(usage, input_per_million, output_per_million):
    # 教学费率由调用者提供，不能当成当前供应商价格。
    return (usage["input_tokens"] * input_per_million +
            usage["output_tokens"] * output_per_million) / 1_000_000

if __name__ == "__main__":
    model = MockModel()
    messages = [{"role": "system", "content": "只依据已给制度回答"},
                {"role": "user", "content": "如何申请VPN？"}]
    result = model.complete(messages)
    print(result["text"])
    print(f"模拟usage：{result['usage']}")
    print(f"教学费率估算：{estimated_cost(result['usage'], 1, 2):.6f}")
```

## 代码执行过程与逐段解释

1. MockModel实例不建立网络连接，complete使用最后一条消息。
2. 返回字典有统一text与usage；真实适配器要处理字段缺失与非文本内容。
3. 20与10是预设用量，仅演示计费公式，不能推断中文token数。
4. estimated_cost把教学费率按百万token换算为单次费用。
5. 默认脚本结束；只有显式运行integration才可能产生真实付费请求。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

适配器类似Java SPI或策略接口；内部业务依赖统一complete契约，不直接依赖HTTP响应字段。Python采用鸭子类型，相同方法可替换，无需所有类继承同一基类。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 把字符数当token数：实际用供应商usage，预算留出输出空间。
- 200当回答可靠：另做证据与任务质量评估。
- 超时立即重试付费请求：响应可能已产生，需考虑重复成本与供应商请求标识。
- 密钥写进代码：integration从环境变量读取，错误输出不记录密钥或完整响应。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data包含usage与budget，按给定input_rate/output_rate计算教学费用；输入token必须非负整数，拒绝bool；费用超预算返回deny，否则allow。不得真实调用模型。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/08-model-api/exercises/practice.py
python lessons/08-model-api/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

后续把重试、超时、模型路由和费用追踪放在统一边界。先保留每次调用的模型、请求ID和usage，再区分接口可用性、任务正确率与安全性。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://developers.openai.com/api/reference/resources/chat)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

真实接入见 [HTTP适配器](integrations/README.md)。2026-10-06核查官方Chat接口资料；使用标准库urllib，不引入SDK版本依赖。该适配仅覆盖OpenAI Chat Completions形状及明确兼容的端点，不兼容所有供应商或Responses API。

## 真实接口与模拟接口怎么切换

业务依赖 `model.complete(messages)`，模拟与HTTP适配实现相同方法名和内部返回结构。
这里统一的usage字段允许None，表示供应商未报告；未知用量不能按0计费。
真实HTTP响应的prompt_tokens/completion_tokens由适配器转换为内部input_tokens/output_tokens。
不要在业务层散布供应商JSON路径，也不要为了兼容把拒答吞成空字符串。
不同API的工具调用、消息角色、流事件与参数支持不同，先核查再增加显式适配。

## 认证头与重定向边界

初始URL为HTTPS仍可能收到跨源或降级跳转；只校验初始地址不够。
本项目Python 3.12.10的urllib默认处理部分POST重定向时保留Authorization。
本课真实适配用私有opener在默认重定向处理前拒绝300—399全部响应，包含307/308。
它关闭原响应并返回明确接口失败，既不读取跳转目标，也不发送第二次请求。
调用者应确认最终HTTPS端点后配置地址；错误中不展示Token、Location和响应正文。
`RejectRedirects`继承HTTPErrorProcessor；`super()`将正常响应交给基类处理，HTTPS方法复用相同门禁。
8个离线测试方法通过，其中一个枚举100种3xx；仅用假Token，未使用真实密钥或访问外网。
详情见[真实接入讲解](integrations/README.md)，官方依据见[urllib处理链](https://docs.python.org/3.12/library/urllib.request.html)。
