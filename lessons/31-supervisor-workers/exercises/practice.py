"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def summarize_required(tasks, results):
    """TODO：将必需和可选子任务区分；必需缺失阻止完成，可选缺失记录warning；重复task id定义为同一个逻辑任务。"""
    # 在这里实现练习；先写边界预期，不要复制参考答案。
    raise NotImplementedError("请完成本课独立练习")

if __name__ == "__main__":
    print("练习骨架已加载：请按exercises/README.md实现函数，再添加自己的调用样例。")
