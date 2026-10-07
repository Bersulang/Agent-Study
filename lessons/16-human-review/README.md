# 阶段 16：澄清、审批与结果检查

## 使用场景

创建工单前，用户要看到具体标题和工具动作。批准某份草稿不代表批准之后被模型改写的草稿；拒绝或过期必须阻止写入。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 15 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

审批和拒绝记录纳入单Agent主项目：批准绑定用户/租户、动作、参数摘要和有效期限；修改参数或撤销/过期后，原批准不可复用。

### 1. 澄清、编辑与审批

澄清补全缺失参数，编辑改变草稿，审批决定是否允许一个具体动作执行。

用途与例子：修改title后生成新审批请求，旧批准不能复用。

### 2. 内容摘要与绑定

规范化JSON生成稳定字节，哈希摘要绑定工具名与参数内容。

用途与例子：字典键顺序不影响摘要；title改变会改变摘要。哈希不证明审批人身份。

### 3. 拒绝、过期与转人工

拒绝是终止写入的决策；期限避免旧批准无限有效；无法判定时转人工。

用途与例子：decision=reject时authorized为False，now超过expires_at也为False。

### 4. 检查与有限修订

检查对结果和证据指出具体缺陷；修订应有次数上限，不能循环到检查器满意。

用途与例子：缺来源或字段不完整要求修订，最多一次；未修复转人工，而不是自动补造证据。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/16-human-review/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
原动作允许：True
编辑后允许：False
拒绝后允许：False
结果检查：['没有可核查依据']
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""审批内容绑定演示；审批对象假定来自受信任的人审服务。"""
import hashlib
import json

def action_digest(action):
    # 排序键与固定分隔符保证等价字典产生一致字节序列。
    payload = json.dumps(action, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def make_approval(action, decision="approve", now=0):
    if decision not in ("approve", "reject"):
        raise ValueError("审批决策必须为approve或reject")
    return {"digest": action_digest(action), "decision": decision,
            "expires_at": now + 60, "reviewer": "教学审核人"}

def authorized(action, approval, now=0):
    # 实际服务还要认证身份、查可信审批记录、撤销状态和单次消费。
    return (approval.get("decision") == "approve"
            and now < approval.get("expires_at", 0)
            and approval.get("digest") == action_digest(action))

def review_result(draft, evidence_ids):
    issues = []
    if not isinstance(draft.get("title"), str) or not draft["title"].strip():
        issues.append("标题缺失")
    if not evidence_ids:
        issues.append("没有可核查依据")
    return issues

if __name__ == "__main__":
    action = {"tool": "create_ticket", "args": {"title": "登录失败"}}
    approval = make_approval(action, now=10)
    print(f"原动作允许：{authorized(action, approval, now=11)}")
    edited = {"tool": "create_ticket", "args": {"title": "改过的标题"}}
    print(f"编辑后允许：{authorized(edited, approval, now=11)}")
    denied = make_approval(action, decision="reject", now=10)
    print(f"拒绝后允许：{authorized(action, denied, now=11)}")
    print(f"结果检查：{review_result({'title': '登录失败'}, [])}")
```

## 代码执行过程与逐段解释

1. action包含具体tool与args，先展示给人，再由受信任审核路径生成approval。
2. action_digest排序JSON键，编码UTF-8，计算SHA-256摘要。
3. make_approval保存摘要、决策与过期时刻，教学now是可控整数时间。
4. authorized同时检查批准、未过期、内容相同；任何一个不满足都禁止执行。
5. 修改后的title产生不同摘要，旧批准失效；review_result指出缺证据但不制造证据。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

可类比Java审批单与业务参数快照；MessageDigest计算摘要也无法认证审批人。Pythonjson.dumps规范化适用于本课简单JSON值，跨语言签名需要统一规范，不能随意依赖浮点序列化。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 只批准“创建工单”：必须绑定具体参数和动作。
- 哈希当签名：任何人可自行计算，可信审批记录和身份认证不可省略。
- 拒绝后继续写入：拒绝应阻止副作用，转人工不能绕过拒绝。
- 过期边界使用<=：本课now等于expires_at即失效，应有测试。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data含action/approval/now，先检查决策、摘要和期限，再返回execute或blocked；只能create_ticket且title非空。增加“拒绝原因”和一次有限修订流程：无证据则human_review，不伪造引用。不得真实写工单。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/16-human-review/exercises/practice.py
python lessons/16-human-review/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

审批必须来自可信身份与服务端记录，本例不能作为防伪授权凭证。生产还要撤销、单次消费、重放保护、幂等键与审计。结果检查应列具体依据，限制修订次数并保留改动前后版本。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/hashlib.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/16-human-review/tests -v`。本例没有认证服务器，不声称防伪、持久化或生产审批安全。

## 安全边界与有限修订

SHA-256只检测内容一致，不能证明是谁批准，不能防止伪造整个approval字典。
本课make_approval是假定已完成人审后的可信内部动作，不是允许模型自行批准。
生产服务应加载可信审批记录，并在同一执行事务里验证有效期、撤销、摘要和消费状态。
当前示例没有单次消费与撤销记录，因此只教学内容绑定，不作为生产授权方案。
结果检查返回具体issues；一次修订未修复则转人工，不能用生成的引用冒充真实依据。
审批时刻用可注入的now便于边界测试；生产需统一可信服务时钟与时间单位。
