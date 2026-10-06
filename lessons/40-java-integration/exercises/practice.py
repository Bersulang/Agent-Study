"""完成独立练习后再阅读参考实现；演示模块提供已有接口。"""
import importlib.util
from pathlib import Path

# 路径以当前文件为锚点，因此从项目根目录运行也能加载同阶段代码。
spec = importlib.util.spec_from_file_location("lesson_demo", Path(__file__).resolve().parents[1] / "examples" / "demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

def classify_http_error(status):
    """TODO：将401标为authentication、403为authorization、404为not_found、429/503为retryable_read，其他为permanent；只读重试不代表写入安全。"""
    # 在这里实现练习；先写边界预期，不要复制参考答案。
    raise NotImplementedError("请完成本课独立练习")

if __name__ == "__main__":
    print("练习骨架已加载：请按exercises/README.md实现函数，再添加自己的调用样例。")
