# 阶段 39：FastAPI服务与事件接口

## 使用场景

命令行助手需要提供创建任务、查询进度、取消和断线后重连的HTTP接口。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能运行真实FastAPI应用与TestClient，区分事件类型并验证非法请求无副作用。

- 真正先修：能用03函数组织业务接口、04异常处理失败，并理解13—16消息/循环/状态/审批的基本概念。阶段38可提前预习或在服务后正式比较，不是本课硬前置。
- 本课是单Agent企业服务主线的入口；先完成39—43核心闭环，再选择进入37 A2A远程专项或深化多Agent模式。
- 集成验收需有真实FastAPI应用的HTTP/事件/取消/重连证据；离线机制须由学员独立验收通过后，才能记机制已通过，真实集成仍待验收。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念：入口校验、任务状态与续读游标

离线`TaskService.create`先验证session和prompt，成功后才分配task id并创建running任务，初始事件只有progress。advance只处理running，追加text/final并终结；cancel先改状态并追加canceled，因此随后advance不会生成final。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
if task["status"] == "running":
    task["events"].extend(["text", "final"])
    task["status"] = "completed"
```

<details><summary>先预测：空prompt创建任务后tasks有几条？</summary>

0，因为校验先于分配和写入。取消案例事件为progress、canceled。练习`after`表示最后已收到的序号，只返回更大的seq；session不匹配必须拒绝，不能当空事件列表。

</details>

示例是领域层字典，不是HTTP server。真实FastAPI路由、TestClient、SSE和取消/续读在integrations单独验收；离线机制由学员独立验收通过后，才能记机制通过。SSE的断线重连需有稳定序号，不能依赖连接内存游标。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/39-fastapi-service/examples/demo.py
python -m unittest discover -s lessons/39-fastapi-service/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 'completed', 'events': ['progress', 'text', 'final']}
cancel {'status': 'canceled', 'events': ['progress', 'canceled']}
invalid {'error': 'invalid_request', 'tasks': 0}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
"""离线服务领域层。实际 FastAPI 路由、事件流及页面见 integrations。"""
class TaskService:
    def __init__(self):
        self.tasks = {}

    def create(self, session_id, prompt):
        if not isinstance(session_id, str) or not session_id.strip() or not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("invalid_request")
        task_id = f"task-{len(self.tasks) + 1}"
        self.tasks[task_id] = {"session": session_id, "status": "running", "events": ["progress"]}
        return task_id

    def advance(self, task_id):
        task = self.tasks[task_id]
        if task["status"] == "running":
            task["events"].extend(["text", "final"])
            task["status"] = "completed"

    def cancel(self, task_id):
        task = self.tasks[task_id]
        if task["status"] != "running":
            raise ValueError("task_not_cancelable")
        task["status"] = "canceled"
        task["events"].append("canceled")

    def read(self, task_id):
        task = self.tasks[task_id]
        return {"status": task["status"], "events": list(task["events"])}

def run_case(case):
    service = TaskService()
    try:
        key = service.create("session-7", "" if case == "invalid" else "查询工单")
    except ValueError as exc:
        return {"error": str(exc), "tasks": len(service.tasks)}
```

按执行顺序追踪：

1. TaskService是领域层，默认程序不需要第三方依赖。
2. create验证后才生成id并写tasks。
3. advance仅处理running任务，因此取消后不生成最终结果。
4. read返回events拷贝，调用者不能通过列表引用篡改事件。
5. integrations app用路由装饰器注册接口，TestClient在进程内真实调用ASGI应用。


### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

FastAPI路径装饰器类似Spring的@RequestMapping，Pydantic类似Bean Validation；Python注解由框架读取校验，普通函数注解不会自动校验。

## 易错点与排查

- 把text当最终结果触发业务写入：要等待明确final。
- 每次重连创建新任务：会重复执行，应复用task id与事件序号。
- BackgroundTasks当可靠队列：进程退出会丢任务。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`replay_events(service, task_id, session_id, after)`。

实现会话隔离和事件续读：session不匹配拒绝；after为已收到序号，只返回后续事件；负序号拒绝。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/39-fastapi-service/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“请求校验”与“会话与任务”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；统一校验会自动保存运行命令与结果，练习验收提问仍需独立解释。
3. 手工预测`invalid`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

集成页面仅供本地教学；生产还需要真实用户身份、持久事件日志、背压、代理缓冲设置与Worker队列。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

实际FastAPI应用、TestClient测试和交互页面见[integrations/README.md](integrations/README.md)。
安装固定依赖后先运行接口测试，再启动`integrations/app.py`并打开本地页面。
页面的“推进”按钮是手工模拟Worker完成；生产后台执行需要阶段42的可靠领取机制。

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [FastAPI测试](https://fastapi.tiangolo.com/tutorial/testing/)及[流式响应](https://fastapi.tiangolo.com/advanced/custom-response/)：真实接口边界。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 39`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
