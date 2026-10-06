# 阶段 01：观察实际运行环境，用于排查解释器和路径问题。
# 只读取环境信息，不访问网络，不读取密钥，不修改文件。

# platform 是 Python 标准库的一部分，用来获取版本和平台信息。
import platform

# sys 提供当前 Python 解释器的相关信息。
import sys

# pathlib 用于处理路径；这里导入 Path，读取当前工作目录。
# “from 模块 import 名字”的语法在讲义中说明，后续模块课程会展开。
from pathlib import Path

# 括号表示调用：python_version() 会返回版本文本。
# print 中用逗号分开多个内容，默认用一个空格连接后输出。
print("Python 版本：", platform.python_version())

# executable 是属性，读取它无需加括号；路径是判断环境的重要依据。
print("解释器路径：", sys.executable)

# cwd() 读取程序启动时的当前工作目录，它不一定是脚本所在目录。
print("当前工作目录：", Path.cwd())

# != 表示“不相等”，比较结果为 True（成立）或 False（不成立）。
# 常规 venv 中，当前环境前缀与基础环境前缀不同，可用于确认环境。
print("使用虚拟环境：", sys.prefix != sys.base_prefix)
