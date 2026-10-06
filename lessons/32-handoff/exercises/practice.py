"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def safe_handoff(owner, target, facts, history):
    """TODO：扩展为reader与ticket两类接收者，分别校验question和ticket_id；缺失字段返回needs_clarification；不能改变输入事实。"""
    # 在这里实现练习；先写边界预期，不要复制参考答案。
    raise NotImplementedError("请完成本课独立练习")

if __name__ == "__main__":
    print("练习骨架已加载：请按exercises/README.md实现函数，再添加自己的调用样例。")
