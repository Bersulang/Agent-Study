# 实际LangGraph迁移

默认手写状态机帮助理解机制，本目录使用真实langgraph==1.2.13。2026-10-06核查官方中断与状态图文档。

项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/27-langgraph/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/27-langgraph/integrations/langgraph_demo.py
```

预期先打印paused与T1动作，再打印resumed包含rejected；第二线程accepted包含done。脚本有限退出，不需要模型密钥。

## 从手写流程映射到SDK

| 手写机制 | LangGraph机制 | 本例职责 |
|---|---|---|
| 字典状态 | TypedDict + StateGraph | 描述task、approved、status |
| step分支 | add_node + add_edge | review节点等待决定 |
| if选择后继 | add_conditional_edges | route选择accepted或rejected |
| 局部流程函数 | compile后的子图 | accepted封装finalize |
| 保存进度 | InMemorySaver | 以thread_id保存暂停状态 |
| waiting与继续参数 | interrupt + Command(resume=...) | 外部决定恢复同一线程 |

TypedDict是类型说明，total=False允许阶段字段尚未出现；它本身不校验恶意输入。
`@`装饰器本例不需要。`StateGraph(State)`是构造器，add_node注册函数但不执行，compile形成可运行图，invoke才实际执行。
节点返回局部字典更新；没有显式reducer的字段覆盖原值。不要在节点里任意修改传入state的嵌套对象。
START和END是框架特殊标记，不是模型工具名。条件边返回下一个节点标识，不应在路由里写数据库。

## 中断与副作用

interrupt之前的代码恢复时可能重跑。检查点只保存状态，不能保证外部写入自动去重。
先暂停审批，外部系统核查具体动作摘要，再恢复；业务写入仍需要幂等键与可信授权。
thread_id隔离任务状态；恢复必须使用相同thread_id，换线程会创建新的执行上下文。
InMemorySaver进程结束丢失记录；本例验证同进程暂停恢复，没有验证持久数据库或故障恢复。
用相同输入对照手写流程与图，比较拒绝、批准、缺少决定三种状态；框架应保留业务语义。

- [LangGraph中断](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph子图](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)
- [LangGraph持久化](https://docs.langchain.com/oss/python/langgraph/persistence)
