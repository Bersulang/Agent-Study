# 阶段 23：上下文工程

## 使用场景

长对话挤满无关工具结果，系统仍要记住审批要求并保留当前问题的证据。

主线项目是企业知识与工单协作助手。本阶段只增加一个可解释的能力边界，先验证机制，再讨论规模化。
运行演示不需要模型密钥，也不会请求真实业务系统。

## 学习目标

- 能按优先级追踪选择、裁剪及字符预算累计，并指出必要上下文放不下时的失败。
- 能说明字符数只是token容量的教学代理，以及外部证据为何不能自授required权限。
- 能设计带source的data包装，确保资料内容不会变成system指令。

## 前置知识

建议先读阶段13消息历史与阶段16审批约束；如果尚未完成它们，可把rule、evidence和history当普通字典阅读，不阻塞本课离线练习。

## 概念：优先级决定取舍，必要约束不能被悄悄删掉

模型上下文有容量上限。`pack`按priority从高到低考虑每条内容，使用文本字符数作为本课容量代理；放得下就复制到selected并累计used，放不下的普通历史放入dropped。若放不下的项目标记`required=True`，函数抛错，而不是悄悄丢掉审批规则。

下面摘录或简化本课示例的关键步骤，需结合[完整源码](examples/demo.py)中的定义与上下文阅读；运行时使用下方演示命令。

```python
cost = len(item["text"])
if used + cost <= budget:
    selected.append(dict(item))
    used += cost
elif item.get("required", False):
    raise ValueError("必要上下文放不下，不能静默裁剪约束")
```

演示容量是8。`rule`文本“必须审批”长度4，先放入；`evidence`“发票有效”也是4，刚好填满；较长的history只能被丢弃。注意检索到的证据不能自己声明为required来压过可信规则：required标记应由组装上下文的受信任程序决定。

<details><summary>展开推导：若把budget改成7，规则仍需4字符，证据要4字符，函数返回什么？</summary>

规则先入选，used变为4；证据再考虑时4+4大于7。它不是required，所以记录在dropped；最终used为4。若容量改成3，规则本身放不下且required为True，函数会抛ValueError，调用方必须调整预算或停止任务，不能伪造“规则已送入模型”。字符数只是教学代理，不等于token数。
</details>

Java对照：可以把上下文项建模为不可变record并显式区分可信约束、证据和历史。优先级排序解决容量取舍，不代表低优先级信息错误；生产截断前应记录被移除内容和预算原因。

## 演示文件与执行命令

默认工作目录是项目根目录 `C:\Users\Mason\Desktop\agent-study`。
如已创建虚拟环境，可以把python替换成 `.\.venv\Scripts\python.exe`，无需激活或修改执行策略。

```powershell
python lessons/23-context-engineering/examples/demo.py
python lessons/23-context-engineering/solutions/solution.py
python -m unittest discover -s lessons/23-context-engineering/tests -v
```

第一条运行演示；第二条仅在完成练习后阅读与运行；第三条执行本阶段行为检查。
`-m`表示让解释器把模块当入口，`discover`搜寻test_开头文件，`-s`指定测试目录，`-v`显示每个测试名字。
测试正常时结尾是 `OK`。故意运行未完成的练习函数出现NotImplementedError，代表你还需要实现，不代表环境坏了。

### 默认演示预期输出

```text
{'selected': [{'id': 'rule', 'text': '必须审批', 'priority': 100, 'required': True}, {'id': 'evidence', 'text': '发票有效', 'priority': 50}], 'dropped': ['history'], 'used': 8}
```

### 预期输出如何阅读

rule优先级最高且长度8，evidence长度4；budget=8只能装下rule，因此history被记录在dropped，used保持8。这里计量的是字符数，不是模型token；必需项放不下会raise而不是静默删除。

## 执行过程与状态变化

1. 上下文按优先级稳定排序。
2. 按字符代理计算容量。
3. 必要约束无法放入则停止。
4. 可选内容被裁剪并显式记录。

排序后逐项尝试放入，命中预算才复制到selected并累加used。`dict(item)`是浅复制：本例只调整外层记录，嵌套内容没有深拷贝。required放不下时直接raise，避免返回一个看似成功但缺关键约束的上下文。

## 逐行阅读与Python语法

`sorted(..., key=lambda item: -item["priority"])`返回新列表，不改输入顺序；优先级相同保持原先相对顺序。`item.get("required", False)`让缺省字段按可选处理，但练习的外部证据不应信任它自己填required。

## 对照源码的逐行解释

按examples/demo.py中的顺序阅读，下列关键表达式决定正常与失败路径。

| 表达式或位置 | 为什么这样写及状态变化 |
|---|---|
| `sorted(...priority...)` | 返回新列表，原items顺序不被修改；同优先级保留原顺序。 |
| `len(text)` | 这里按字符数计费，中文一字不一定等于一个token；真实模型预算必须用匹配tokenizer。 |
| `used + cost <= budget` | 恰好等于预算允许放入，下一项可能被裁剪。 |
| `required` | 必要指令与身份约束放不下直接raise，不能默默删除审批要求以完成请求。 |
| `dropped列表` | 让取舍可观察，复核丢弃的是闲聊还是任务所需证据；字段默认False通过get实现。 |
| `贪心边界` | 逐项放入不是全局最优背包算法，长高优先级证据可能挤掉多个短片段；必要内容应设计更高优先级。 |
| `摘要边界` | 摘要保留任务号、当前约束、未解决问题和引用位置，不能把过去工具错误摘要成成功事实。 |

## Java Web对照

Java可用不可变消息类型区分system与data；真实tokenizer要按模型计算容量。本课按字符长度排序裁剪，不是供应商token计数。

## 易错点与排错顺序

1. 文件路径错误：确认终端在项目根目录，先运行演示而不是练习骨架。
2. 把空结果当成功：查返回状态与来源，不能编造缺失字段或证据。
3. 在失败后继续修改：先验证再变更，给失败输入补行为测试。
4. 共享可变对象：调用前后打印输入，确认是否被无意修改。
5. 把模拟效果当生产质量：检查本页边界说明与真实接入目录。
6. 只看最终回答：保留查询、状态或执行轨迹，定位失败发生在哪一步。

## 独立练习

增加不可信证据包装：source与text进入独立data字段，不能生成system角色；预算仍计算包装后的实际文本长度。

打开 [练习要求](exercises/README.md)，在 [practice.py](exercises/practice.py) 实现。
骨架有意留下待实现函数，示例和参考答案不能替代你自己的思考与测试。
自动校验保存包装和预算结果；概念验收仍需指出字符代理、可信角色和权限校验各自能证明什么。

## 能力验收

- 能不看代码解释至少三个概念，并各举一个企业助手场景。
- 能预测演示执行前后的关键字段，再通过运行核对。
- 能独立修改一项业务规则并解释对结果的影响。
- 能让一个失败输入按预期被拒绝，且不产生越权或错误证据。
- 能说明本课测试证明了什么、没有证明什么。

材料制作、代码验证、学员掌握是三种状态；本课提供材料与验证方法，学员能力仍待验收。

## 工程延伸与边界

字符预算不是token预算，标签包装不能单独防住提示注入；生产需真实tokenizer、可信角色分离与工具权限校验。

从本课迁移到企业项目时，先写输入输出契约与独立评估案例，再决定存储、模型和框架。
保留可追溯来源和任务/身份信息，让问题能定位到具体数据与步骤。
添加性能优化前先检查正确性，尤其是失败时是否仍保护权限、预算和有效状态。
单元测试覆盖本地规则；真实网络、持久化、并发与供应商行为需要额外集成验证。

## 官方资料与复习

- [本课官方参考](https://docs.langchain.com/oss/python/langchain/context-engineering)：查API或协议边界，不要求一次读完。
- [Python 3.12教程](https://docs.python.org/zh-cn/3.12/tutorial/)：复习循环、函数、异常和模块。
- [本课知识卡](knowledge.md)：按定义、案例、误区整理。
- [验证记录](verification.md)：仅记录实际执行范围，不能据此声称生产部署通过。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 23`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
