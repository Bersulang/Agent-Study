# 阶段 16：澄清、审批与结果检查

## 使用场景

创建工单前，用户要看到具体标题和工具动作。批准某份草稿不代表批准之后被模型改写的草稿；拒绝或过期必须阻止写入。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能说明审批绑定的是哪一份动作快照，并用参数编辑验证旧审批失效。
- 能区分哈希的一致性用途与身份认证用途。
- 能预测拒绝、过期、内容变更和缺少证据时是否允许执行或转人工。

## 前置知识与阅读顺序

先完成阶段 15 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

审批和拒绝记录纳入单Agent主项目：批准绑定用户/租户、动作、参数摘要和有效期限；修改参数或撤销/过期后，原批准不可复用。

审批安全的关键不是“有一张approve字典”，而是批准必须对应将要执行的精确动作。演示把工具名与参数放在同一个`action`对象里，再排序序列化后计算摘要：

```python
payload = json.dumps(action, sort_keys=True, separators=(",", ":"))
digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

排序使键顺序不同但内容相同的字典得到相同字节。把title改成另一句话，摘要就改变，`authorized`拒绝复用旧批准。先预测：`now == expires_at`是否有效？无效，因为条件是`now < expires_at`。

拒绝也是明确决策；不能把decision从reject改成approve继续执行。`review_result`只报告“没有可核查依据”，不会替学员或模型造引用。练习里的有限修订应保留原草稿和新版本，超过上限后转人工。

反例：哈希不是数字签名。任何人都能为伪造的approval重新计算摘要；本例假设审批对象来自可信人审服务，因此不能拿它直接授权生产写入。生产还需要身份认证、可信存储、撤销、单次消费和重放保护。

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

正常路径按顺序检查决策、期限与摘要：approve且未过期且摘要相同才返回True。编辑参数后只改变摘要这一项，也足以使结果变False；拒绝后即使摘要和期限都匹配仍为False。

## Java 对照

可类比Java审批单保存的参数快照，再用`MessageDigest`检查快照一致性。Java和Python都不能靠摘要证明审核人身份；跨语言签名还必须统一JSON规范、编码和时间单位。本例的`json.dumps`只适合说明简单数据的排序序列化。

## 易错点与排查

- 只批准“创建工单”：必须绑定具体参数和动作。
- 哈希当签名：任何人可自行计算，可信审批记录和身份认证不可省略。
- 拒绝后继续写入：拒绝应阻止副作用，转人工不能绕过拒绝。
- 过期边界使用<=：本课now等于expires_at即失效，应有测试。

若未编辑动作却摘要不一致，检查序列化规则是否固定；若编辑后仍允许，检查摘要是否包含args；若过期边界出错，重点验证等于expires_at的时刻。

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
5. 自动校验保存运行命令、输出和案例结果；失败修复过程用于解释，不要求手工粘贴输出。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 16`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
