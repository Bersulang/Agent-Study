# 阶段 01：开发环境与第一个企业助手程序

导航：[项目首页](../../README.md) · [知识手册](../../docs/knowledge.md) · [学习进度](../../docs/progress.md)

## 1. 业务场景：先让未来的助手启动

我们最终要开发企业知识与工单协作助手。现在先完成最小要求：程序能够启动，显示名称和当前能力，并且能确认它使用了哪个 Python 环境。

这一课没有模型调用。先把运行和调试机制学清楚，后面出现“包已经安装却无法导入”“编辑器运行失败”等问题时，才有排查依据。

## 2. 本课目标与学习顺序

完成后，你应当能够：

- 区分终端、解释器、编辑器和源代码文件。
- 创建项目虚拟环境，确认实际使用的解释器。
- 独立运行并修改 `.py` 文件。
- 解释 `print`、字符串和注释。
- 定位路径错误，在编辑器中设置断点。
- 说明 Git 的基本工作方式。

按“先看概念 → 跑示例 → 改程序 → 排查错误 → 做练习 → 验收”的顺序学习。第一次可以分几次完成，不要求一天内学完。

## 3. 四个概念先分清

| 概念 | 用途 | 你熟悉的联系 |
| --- | --- | --- |
| 终端 / PowerShell | 输入并执行系统命令 | 类似你在终端运行 Maven 或 Java 命令 |
| Python 解释器 | 执行 Python 代码 | 可先与 Java 运行时建立联系，但机制不完全相同 |
| 编辑器 / IDE | 写代码和调试 | 类似 IntelliJ IDEA |
| `.py` 文件 | 保存 Python 源代码 | 类似 `.java` 保存源代码 |

下面是 **PowerShell 命令**，输入终端：

```powershell
python --version
```

下面是 **Python 代码**，保存到 `.py` 文件或输入 Python 交互模式：

```python
# 调用输出功能，显示括号中的字符串。
print("企业知识与工单助手")
```

如果终端显示 `>>>`，你处于 Python 交互模式，输入 `exit()` 回到 PowerShell。不要把文件运行命令输入 `>>>`。

Python 也存在编译与字节码机制；这里先掌握实际使用方式，不将它理解为“完全没有编译”。

### 一条运行命令实际上经过哪几步

在编辑器中看到源代码，不表示它已经执行。保存文件后，PowerShell先理解你输入的命令，找到指定的Python解释器，再由解释器读取脚本、检查语法并执行。输出最终回到终端。这里有两个不同的问题：PowerShell能不能找到解释器？解释器能不能找到并运行脚本？

```text
保存.py文件 → PowerShell解析命令 → 启动指定Python → 读取脚本 → 执行print → 终端显示文字
```

所以“找不到python”与“can't open file”不是同一层的问题。前者还没有成功启动解释器，后者通常是解释器已经启动，却无法打开指定文件。先定位出错层次，再决定查安装路径还是查脚本路径。

**先预测：** 你在编辑器中改了卡片但还没保存，然后从终端重新运行，看到的是新文字还是旧文字？

<details>
<summary>查看原因</summary>

通常看到磁盘上旧文件的文字，因为终端启动的解释器读取已保存文件，不会读取编辑器尚未保存的缓冲区。如果编辑器有自动保存，要先核对它是否已经替你保存。验证时用实际文件内容判断，不靠猜测。

</details>

## 4. 确认目录与已有环境

所有操作从项目根目录开始，在 PowerShell 执行：

```powershell
cd C:\Users\Mason\Desktop\agent-study
Get-Location
python --version
python -m pip --version
git --version
```

逐条解释：

- `cd`：切换当前工作目录。
- `Get-Location`：显示当前工作目录，结果应是本项目路径。
- `python --version`：显示当前命令找到的 Python 版本。
- `python -m pip --version`：使用这个 Python 的 pip 显示版本和安装位置。
- `git --version`：检查 Git 是否可用。

课程制作时使用 Python 3.12.10。现在以你运行命令看到的结果为准；版本与路径符合要求时，不需要重新安装。即使另有环境管理工具，本课也先理解内置的 `venv` 与 pip。

## 5. 为项目创建虚拟环境

### 为什么需要它

假设两个项目需要不同版本的模型 SDK，全部安装到同一个环境会难以管理。虚拟环境为项目提供独立的依赖安装位置。

它与 Maven 的依赖管理有部分联系，但不等价：虚拟环境不自动生成依赖版本清单，也不是 Docker，不限制程序访问文件和网络。

### 创建与检查

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

解释创建命令：

- `python`：运行当前找到的 Python。
- `-m venv`：让 Python 执行内置的 `venv` 模块；模块先理解为一组可使用的代码。
- `.venv`：创建出来的环境目录名称。

环境如果已由助手创建，你仍需要理解命令并自己做检查。日常不必每次运行程序都重新创建。

再执行：

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

`-c` 表示执行后面的短代码；`import sys` 导入读取解释器信息的模块；`sys.executable` 是当前解释器路径；分号在这里用来分隔两条短语句，普通 Python 文件更建议分行。

输出应以本项目的 `agent-study\.venv\Scripts\python.exe` 结尾。**是否在项目虚拟环境中运行，要看实际路径。**

### 激活是可选的

激活可以让当前终端中的 `python` 更方便地指向虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
```

离开激活状态可执行 `deactivate`。激活影响当前终端，不代表另一窗口或编辑器也使用相同解释器。

如果激活被 PowerShell 执行策略阻止，继续使用 `.\.venv\Scripts\python.exe` 的完整路径即可。本课不需要修改系统执行策略。

## 6. 跑通第一个示例

文件：[examples/hello_agent.py](examples/hello_agent.py)。

```powershell
.\.venv\Scripts\python.exe .\lessons\01-environment\examples\hello_agent.py
```

预期输出：

```text
企业知识与工单助手
当前版本：只展示启动信息
下一步：学习如何接收和处理工单
```

命令的前半部分指定解释器，后半部分指定它要执行的文件。`./` 或 Windows 下的 `.\` 表示从当前目录开始。

### 逐行讲解

```python
# 告诉使用者：这个程序是什么。
print("企业知识与工单助手")
```

- `#` 后面的内容是注释，不执行；这里解释输出的目的。
- `print` 是 Python 提供的输出功能。
- `(...)` 表示调用，把括号里的内容交给这个功能。
- `"企业知识与工单助手"` 是字符串，也就是文本。
- 引号和括号要使用英文符号，字符串里的中文没有问题。

后面两条 `print` 用法相同。Python 从上到下依次执行。相较 Java 的 `System.out.println(...)`，这里不用类和 `main` 方法，也不用在行末加分号。

### 跟着改一次

打开示例，只把程序名称改成“我的企业助手”，运行并观察变化。理解后改回原名称，使演示文件与讲义预期结果保持一致。

## 7. 运行环境信息示例

文件：[examples/environment_info.py](examples/environment_info.py)。

```powershell
.\.venv\Scripts\python.exe .\lessons\01-environment\examples\environment_info.py
```

输出会包括：

```text
Python 版本： 3.12.10
解释器路径： ...\agent-study\.venv\Scripts\python.exe
当前工作目录： ...\agent-study
使用虚拟环境： True
```

这里的 `...` 表示省略了机器相关的路径，不是实际输出文字。版本以你的实际环境为准。

### 本示例中的新语法

| 代码 | 含义 |
| --- | --- |
| `import platform` | 导入提供运行平台信息的标准库模块 |
| `import sys` | 导入提供解释器信息的标准库模块 |
| `from pathlib import Path` | 从路径处理模块导入 `Path`；对象机制后续展开 |
| `platform.python_version()` | 调用模块中的功能，返回版本文本 |
| `sys.executable` | 读取解释器路径 |
| `Path.cwd()` | 获取当前工作目录 |
| `sys.prefix != sys.base_prefix` | 比较环境前缀；常规 venv 中不同表示在虚拟环境内 |
| `True` / `False` | 表示判断成立或不成立 |

`print("标签", 值)` 可以输出多个内容，默认用空格分隔。点号用于访问模块或对象里的成员；有括号是调用，没有括号的这些例子是读取属性。

这一示例供你观察和排错，不要求现在独立实现所有环境检测逻辑。

## 8. 工作目录与路径排查

当前工作目录不一定是脚本所在目录。后续读取数据文件时，这个区别尤其重要。

在项目根目录检查：

```powershell
Get-Location
Test-Path .\lessons\01-environment\examples\hello_agent.py
```

第二条应输出 `True`。如果为 `False`，先检查所在目录和文件名。

路径包含空格时，用引号包围；可执行文件路径也包含空格时，在 PowerShell 中用 `&` 调用：

```powershell
& "C:\Users\Mason\Desktop\agent-study\.venv\Scripts\python.exe" "C:\Users\Mason\Desktop\agent-study\lessons\01-environment\examples\hello_agent.py"
```

这里 `&` 是 PowerShell 的调用运算符，不是 Python 语法。

### 用反例区分脚本目录和工作目录

假设你站在项目根目录运行位于`lessons/01-environment/examples/`里的脚本。Python不会因为脚本放在那里，就自动把当前工作目录切换到examples。解释器路径、脚本路径和工作目录是三个独立信息；环境信息示例就是让这三个位置变得可观察。

**先预测：** 两个终端都用同一个`.venv`解释器，但一个从项目根目录启动，另一个从上一级目录启动。解释器路径会相同吗？工作目录会相同吗？

<details>
<summary>查看推导</summary>

若确实指定同一个解释器的绝对路径，解释器路径相同；工作目录取决于各自从哪里启动，所以不同。相对脚本路径也要跟着启动位置改变，否则可能在读取脚本前就失败。后续阶段04读取文件时，还会看到相对数据路径受工作目录影响。

</details>

## 9. 在编辑器中运行与设置断点

你可以使用已经熟悉的编辑器。下面用 VS Code 的常见方式说明；界面标签可能随版本或语言变化。

1. 打开整个 `agent-study` 文件夹，不只打开某个文件。
2. 如果使用 VS Code，确认已启用 Python 扩展；PyCharm 则在项目解释器配置中选择环境。
3. 为项目选择 `.venv\Scripts\python.exe` 作为解释器。
4. 运行 `environment_info.py`，检查路径，不能只凭状态栏名称判断。
5. 打开 `hello_agent.py`，在第一条 `print` 行旁设置断点。
6. 启动“调试 Python 文件”，让程序停在断点。
7. 逐步执行，观察三行输出出现的顺序，再继续到结束。

普通运行和调试启动不同。如果断点没有停住，先检查启动方式和断点所在位置。

本课不要求先配置复杂的调试文件，重点是会选择解释器、启动调试和观察执行。

## 10. Git 入门：保存源代码版本

Git 记录版本。先理解三个位置：

- 工作区：你当前看到和编辑的文件。
- 暂存区：你选择准备放入下一次提交的内容。
- 提交：一次版本快照。

当前项目目录已经位于 Git 仓库中，无需重复运行 `git init`。你可以把下面作为独立操作练习，从项目根目录查看状态并理解暂存区：

```powershell
git status
git add README.md
git diff --cached
```

这里仅暂存 `README.md`，便于理解；没有自动暂存所有内容。实际提交命令是 `git commit -m "docs: add learning entry"`，它创建本地快照，不会推送远程。首次提交如果提示身份未设置，需要配置提交作者；本课不要求你上传仓库或立即提交。

本项目 `.gitignore` 已排除虚拟环境、缓存和真实环境配置。后续遇到 API Key 时，不能把它提交到 Git。

如果你已经初始化，使用 `git check-ignore .venv/pyvenv.cfg` 可以确认环境文件被忽略。`.gitignore` 不会让已跟踪的文件自动停止跟踪，这一点后续会用例子讲。

## 11. 常见错误：按症状排查

| 症状 | 可能原因 | 检查与处理 |
| --- | --- | --- |
| `python` 无法识别 | 命令查找路径或安装问题 | 用 `Get-Command python` 检查；不要先安装第二份 Python |
| `can't open file` | 工作目录不对或脚本路径错误 | `Get-Location`、`Test-Path`，再核对文件名 |
| 激活脚本被阻止 | PowerShell 执行策略 | 直接使用 `.venv` 解释器路径运行 |
| `SyntaxError` | 非英文引号、括号缺失等 | 看报错行及前一行，核对字符与配对 |
| `NameError` | 将文本当成名称，例如漏了字符串引号 | 核对引号；后续再系统学习变量 |
| 编辑器能跑、终端不能跑，或相反 | 使用了不同解释器或工作目录 | 两边运行环境信息示例比较 |
| `>>>` 下输入运行命令失败 | 把终端命令输入 Python 交互模式 | `exit()` 返回终端后执行 |
| `not a git repository` | 目录尚未初始化，或不在仓库内 | 核对目录；只有准备做 Git 练习时才初始化 |

完整错误比“报错了”更有用。反馈时保存命令、目录、完整错误和你已经检查过的项目，不包含密钥或私人数据。

## 12. 独立练习：制作启动卡片

文件：[exercises/startup_card.py](exercises/startup_card.py)。先看要求，再独立编辑。

要求程序依次输出四行：

1. 你自己起的助手名称。
2. 你希望这个程序用于什么。
3. 它目前实际能做什么，例如只展示文字、还没有接入模型。
4. 你下一步想增加什么能力。

只使用注释、字符串和 `print`。给每行输出加说明用途的中文注释。不需要变量、函数或额外依赖。

运行：

```powershell
.\.venv\Scripts\python.exe .\lessons\01-environment\exercises\startup_card.py
```

### 排错练习

在自己的练习中，暂时删除一行的右括号，再运行，观察错误类型和指向的位置。修复后重新运行。不要直接破坏演示文件。

### 环境迁移练习

在项目中创建一个独立练习环境，验证你不依赖已准备好的 `.venv`：

```powershell
python -m venv .venv-practice
.\.venv-practice\Scripts\python.exe -c "import sys; print(sys.executable)"
.\.venv-practice\Scripts\python.exe .\lessons\01-environment\exercises\startup_card.py
```

检查解释器路径应指向 `.venv-practice`。本项目 `.gitignore` 已排除这个练习环境；打开文件确认规则，初始化 Git 后可用 `git check-ignore .venv-practice/pyvenv.cfg` 验证。练习后再决定是否保留，不要提交虚拟环境。

完成后才查看 [参考答案](solutions/startup_card.py)。名称可以不同，关注输出要求和解释是否正确。

## 13. 验收提交

可选填写 [exercises/submission.md](exercises/submission.md) 记录反思或与教学助手的问答；启动卡片由自动校验检查，命令日志自动保存。

自动校验覆盖启动卡片的输出格式、中文注释与占位内容。环境操作、概念解释、排错和断点/Git仍用于独立讲解验收；没有填写反思表不会阻止自动校验。当前示例能运行，不表示你已经通过阶段01。

## 14. 本课回顾与下一阶段

本课的核心是知道“哪个解释器，在什么目录，执行哪个文件”，并能独立修改和排查简单程序。

下一阶段学习变量、条件和数据结构，用工单数据做筛选和统计。我们会沿用当前项目环境，而不是每课重新搭建。

复习入口：[知识手册 K001—K008](../../docs/knowledge.md)。

## 参考资料

- [Python 3.12 解释器使用](https://docs.python.org/zh-cn/3.12/tutorial/interpreter.html)。
- [Python 3.12 虚拟环境与包](https://docs.python.org/zh-cn/3.12/tutorial/venv.html)。
- [VS Code Python 环境](https://code.visualstudio.com/docs/python/environments)。
- [VS Code Python 调试](https://code.visualstudio.com/docs/python/debugging)。
- [Git 基础](https://git-scm.com/book/zh/v2/Git-%E5%9F%BA%E7%A1%80-%E8%8E%B7%E5%8F%96-Git-%E4%BB%93%E5%BA%93)。


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 01`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。

阶段01开放表达规则：依次填写名称、用途、当前能力和下一步目标，但输出不必包含这些标签，也不限制名称或具体规划。自动检查四条非空输出、明显模板占位、重复内容和中文注释；不声称能判断自然语言含义。内容是否贴合题意可在学习对话中讨论，不作为关键词匹配的通过条件。
