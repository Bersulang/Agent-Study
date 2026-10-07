# 阶段 37：跨服务Agent与A2A

## 使用场景

工单能力位于另一个服务，调用者需要发现能力、追踪任务与产物，并知道是否能取消。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能运行官方A2A SDK服务与客户端，区分Agent Card、任务、消息、产物和身份。

- 真正先修：阶段36协作失败与预算、阶段39服务/API基础；同时需要03函数、04异常与05容器。可先完成39—43单Agent核心服务，再回到本课进行A2A远程专项。
- 缺少SDK或可运行服务时先完成离线机制练习，并把真实A2A运行标记为集成待验收。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. Agent Card

定义与用途：远程Agent发布的能力与传输元数据，不是授权凭据。

具体例子：集成服务声明ticket-status技能和JSON-RPC端点。

### 2. Task生命周期

定义与用途：任务有id、上下文和状态，状态不能任意倒退。

具体例子：submitted到completed，或submitted到canceled；终态不再执行。

### 3. 消息与产物

定义与用途：消息承载交互，Artifact是任务产生的正式输出。

具体例子：SDK executor通过TaskUpdater添加T-7工单状态文本产物。

### 4. 协议与认证

定义与用途：A2A标准规定交互对象与方法，认证/授权仍由服务边界实现。

具体例子：integrations使用官方a2a-sdk==0.3.26；默认TaskRegistry只是领域教具。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/37-a2a-remote/examples/demo.py
python -m unittest discover -s lessons/37-a2a-remote/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 'completed', 'artifact': 'T-7: open'}
cancel {'status': 'canceled', 'artifact': None}
unknown {'error': 'task_not_found'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""离线任务生命周期教具；真实 A2A SDK 服务位于 integrations。"""
class TaskRegistry:
    def __init__(self):
        self.tasks = {}

    def submit(self, task_id, text):
        if task_id in self.tasks:
            raise ValueError("task_already_exists")
        self.tasks[task_id] = {"status": "submitted", "text": text, "artifact": None}

    def finish(self, task_id):
        task = self.tasks[task_id]
        if task["status"] != "submitted":
            return  # 终态不能再次执行，例如取消后不能写产物。
        task["status"] = "working"
        task["artifact"] = "T-7: open"
        task["status"] = "completed"

    def cancel(self, task_id):
        task = self.tasks[task_id]
        if task["status"] in {"completed", "canceled"}:
            raise ValueError("task_not_cancelable")
        task["status"] = "canceled"

    def get(self, task_id):
        if task_id not in self.tasks:
            return {"error": "task_not_found"}
        task = self.tasks[task_id]
        return {"status": task["status"], "artifact": task["artifact"]}

def run_case(case):
    registry = TaskRegistry()
    if case == "unknown":
        return registry.get("missing")
    registry.submit("remote-7", "查询工单 T-7")
```

按执行顺序追踪：

1. submit保存任务，重复id被拒绝。
2. finish检查submitted，再经历working并写artifact。
3. cancel只允许未完成任务，取消后finish不做写入。
4. get对未知id给结构化错误。
5. 真实协议集成让SDK处理JSON-RPC封装与状态存储，不能把本地字典叫A2A实现。

逐行阅读时先找输入参数，再找校验条件、状态改变、失败返回，最后找资源清理；不要只从print输出反推过程。

### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

类似Java远程服务发现加长任务接口，但A2A还标准化消息parts、task与artifact；Python SDK类型使用camelCase JSON别名。

## 易错点与排查

- 把自定义POST /agent叫A2A：接口名字不能证明协议兼容。
- Agent Card技能声明等于权限：调用时仍要鉴权。
- 宣称已取消就证明远程副作用没发生：必须定义任务与业务取消边界。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`cancel_terminal(registry, task_id)`。

封装取消为结构化响应：未知任务not_found、终态not_cancelable、可取消任务canceled；不能对completed任务删除产物。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/37-a2a-remote/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“Agent Card”与“Task生命周期”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；保留实际运行命令与结果。
3. 手工预测`unknown`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

教材固定协议0.3以复现API；最新1.x存在迁移差异。跨企业连接需HTTPS、可信发现、授权和SSRF边界；内存store不支持重启。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

真实接入及安装、根目录启动命令见[integrations/README.md](integrations/README.md)。
先运行协议测试和`client.py --local`，再用两个终端运行真实HTTP服务与客户端。
默认领域教具不能替代SDK验证；本地SDK验证也不能证明TLS、生产身份或跨供应商互操作通过。

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [LangChain多Agent模式](https://docs.langchain.com/oss/python/langchain/multi-agent)：用来对比路由、主控及交接，本课未依赖框架。
- [A2A 0.3规范](https://a2a-protocol.org/v0.3.0/specification/)：固定协议版本。
- [官方Python SDK](https://github.com/a2aproject/a2a-python)：真实协议实现。
