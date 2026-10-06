"""真实LangGraph审批暂停与恢复；不调用模型，无业务写入。"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt


class State(TypedDict, total=False):
    # TypedDict描述字典字段形状；total=False允许节点逐步填入字段。
    task: str
    approved: bool
    status: str


def review(state: State):
    # 恢复时节点会从头重新运行，interrupt之前禁止不可幂等的真实写入。
    decision = interrupt({"task": state["task"], "action": "生成只读报告"})
    if not isinstance(decision, bool):
        raise ValueError("审批决定必须是bool")
    return {"approved": decision}


def finish(state: State):
    return {"status": "done" if state["approved"] else "rejected"}


def route(state: State):
    # 条件边只选择节点名；不在路由函数里修改状态或执行业务动作。
    return "accepted" if state["approved"] else "rejected"


def build_graph():
    # 子图可封装稳定局部流程；与父图共享State中的同名字段。
    accepted = StateGraph(State)
    accepted.add_node("finalize", finish)
    accepted.add_edge(START, "finalize")
    accepted.add_edge("finalize", END)
    builder = StateGraph(State)
    builder.add_node("review", review)
    builder.add_node("accepted", accepted.compile())
    builder.add_node("rejected", finish)
    builder.add_edge(START, "review")
    builder.add_conditional_edges("review", route)
    builder.add_edge("accepted", END)
    builder.add_edge("rejected", END)
    return builder.compile(checkpointer=InMemorySaver())


def main():
    graph = build_graph()
    config = {"configurable": {"thread_id": "case-1"}}
    paused = graph.invoke({"task": "T1"}, config)
    assert "__interrupt__" in paused
    print("paused", paused["__interrupt__"][0].value)
    resumed = graph.invoke(Command(resume=False), config)
    assert resumed["status"] == "rejected"
    print("resumed", resumed)
    # 换线程启动另一任务，不能把前一个任务的决定串入新任务。
    other = {"configurable": {"thread_id": "case-2"}}
    graph.invoke({"task": "T2"}, other)
    accepted = graph.invoke(Command(resume=True), other)
    assert accepted["status"] == "done"
    print("accepted", accepted)


if __name__ == "__main__":
    main()
