# 阶段 12：重试、幂等与不确定结果

## 使用场景

创建工单已成功，但网络响应丢了。直接重试可能产生第二张工单。用幂等键把逻辑操作和多次传输区分，并只对可重试错误做有限重试。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能用自己的话解释本课概念，并用输入输出验证。
- 能沿代码执行顺序解释状态如何变化。
- 能处理本课失败案例，区分业务拒绝与程序错误。
- 能独立完成扩展练习，提供实际运行证据。

## 前置知识与阅读顺序

先完成阶段 11 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

本课首次讨论写工具的重试与幂等。从第一项写操作开始，验收就要包含服务端权限、审批绑定的动作和参数、重复提交以及响应不确定场景；写工具不能仅凭模型提出动作直接执行。

### 1. 瞬态错误与永久错误

瞬态错误可能稍后恢复；参数错误和权限错误通常重试无益。

用途与例子：TimeoutError可重试但结果不确定；ValueError、PermissionError直接传播。

### 2. 幂等键与参数绑定

同一逻辑请求重复执行返回相同结果；键必须绑定输入内容。

用途与例子：request-1首次写T1后丢响应；同键同title返回T1，同键不同title拒绝。

### 3. 超时与未知结果

调用超时只说明调用者没及时看到响应，不证明服务端没执行。

用途与例子：先查询幂等记录或使用服务端去重，不能在本地简单捕获超时后换新键。

### 4. 权限、大小与凭证

权限在副作用前检查；结果需要字段与大小限制；凭证不能进入模型上下文。

用途与例子：allowed为教学布尔开关，真实服务必须从可信身份与授权策略得出。

## 演示命令与实际输出

以下命令默认工作目录为项目根目录 `C:\Users\Mason\Desktop\agent-study`。
PowerShell 中 `python` 是解释器命令，后面的路径是要执行的脚本，不是要切换的目录。
如使用项目虚拟环境，可把 `python` 换成 `.\.venv\Scripts\python.exe`。

```powershell
python lessons/12-tool-reliability/examples/demo.py
```

制作时实际执行得到以下离线输出：

```text
最终结果：{'id': 'T1', 'title': '登录失败'}
实际写入数：1
拒绝：同一幂等键不能绑定不同参数
```

这份输出来自固定数据；它是可重复的程序行为，不是真实模型推理结果。

## 演示源码

```python
"""内存幂等教学夹具；模拟写入后响应丢失，不访问网络。"""
class Store:
    def __init__(self):
        self.tickets = []
        self.requests = {}

    def create(self, key, title):
        if key in self.requests:
            old_title, result = self.requests[key]
            if old_title != title:
                raise ValueError("同一幂等键不能绑定不同参数")
            return result.copy()
        result = {"id": f"T{len(self.tickets) + 1}", "title": title}
        # 教学中同步写入两份内存记录；生产必须放同一数据库事务。
        self.tickets.append(result)
        self.requests[key] = (title, result)
        raise TimeoutError("写入成功但响应丢失")

def retry_create(store, key, title, attempts=2, allowed=True):
    if not allowed:
        raise PermissionError("未授权，不执行写入")
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError("attempts必须为1到3整数")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("幂等键不能为空")
    if not isinstance(title, str) or not title.strip() or len(title) > 100:
        raise ValueError("标题长度必须为1到100字符")
    for attempt in range(attempts):
        try:
            return store.create(key, title)
        except TimeoutError:
            # 只重试超时，沿用原键与参数；最后一次仍失败就传播。
            if attempt == attempts - 1:
                raise

if __name__ == "__main__":
    store = Store()
    print(f"最终结果：{retry_create(store, 'request-1', '登录失败')}")
    print(f"实际写入数：{len(store.tickets)}")
    try:
        retry_create(store, "request-1", "改过的标题")
    except ValueError as error:
        print(f"拒绝：{error}")
```

## 代码执行过程与逐段解释

1. Store维护工单列表与幂等键记录；初始都为空。
2. retry_create先校验权限、尝试次数、键和标题。
3. 首次create写入T1并保存幂等结果，随后刻意抛TimeoutError。
4. 重试沿用request-1，create找到记录，核对title后返回同一T1副本。
5. 换title但保留旧键时抛ValueError，不会被超时重试逻辑捕获。

执行时先读取局部输入，再沿分支或迭代更新局部状态，最后输出可核查的结果。
不要只背函数名字：在每个赋值点记录旧值、新值，以及是否影响调用者对象。
代码中的中文注释解释关键边界；从执行入口向上查找调用，能避免把定义误当执行。

## Java 对照

Java服务也需要幂等键与数据库唯一约束；try/catch本身不能做到恰好一次。Python内存字典仅演示语义，进程重启、多线程/多进程竞争时不保证原子性。

Python 使用缩进表示代码块；同一块通常缩进四个空格。
函数调用的圆括号、字典取值的方括号、字符串引号各有不同作用。
Python运行时决定对象类型；类型标注即使存在，也不会自动执行输入校验。

## 易错点与排查

- 重试换新键：服务端视为新操作，可能重复写入。
- 所有异常重试：权限错误不应反复调用。
- 超时认为没写：超时可能发生在写入之后。
- 无限重试：消耗预算且阻塞任务；真实系统采用有限次数、退避、抖动与总期限。

排查顺序：先看异常最后一行，再看本课文件中的调用位置，最后检查输入与前置条件。
不要用 `except Exception: pass` 隐藏失败；保留可定位的错误并给调用者明确结果。

## 独立练习

实现solve(data)：data为重复创建请求列表，每条含key/title；返回唯一工单列表。同键同参数返回原结果，同键不同参数拒绝。允许不同键相同title创建两张；不能把标题当幂等键。

修改 [练习骨架](exercises/practice.py)，具体要求见 [练习说明](exercises/README.md)。
完成后再阅读 [参考答案](solutions/solution.py)，答案文件不是学员作业。

```powershell
python lessons/12-tool-reliability/exercises/practice.py
python lessons/12-tool-reliability/solutions/solution.py
```

## 能力验收

1. 不看答案解释三个核心概念，并指出演示中对应代码。
2. 独立完成练习正常输入，再处理空输入与失败输入。
3. 现场修改一个需求，先预测输出，再运行核查。
4. 用Java经验说明一个相似点与一个重要差异。
5. 提交实际命令、输出和失败修复说明；材料交付不计为学员通过。

## 企业工程延伸

本课幂等存储只在单进程内有效。生产使用持久化唯一约束、参数摘要、操作状态与结果记录；幂等写入与业务写入必须事务一致，恢复阶段再处理未知结果。

本课保留最小机制；真正上线还要结合后续权限、审计、持久化与评估阶段。
扩展时先固定输入输出契约，再增加复杂性，避免把所有责任塞进一个函数。

## 官方资料与教学边界

- [官方参考](https://docs.python.org/zh-cn/3.12/library/exceptions.html)：用于核查本课语言或接口行为。
- [本阶段知识整理](knowledge.md)：复习概念、边界与迁移问题。

测试：`python -m unittest discover -s lessons/12-tool-reliability/tests -v`。本课无真实等待，模拟超时不是性能测量。

## 重试预算具体包含什么

attempts=2表示总共最多调用两次，包含第一次；不是失败后再重试两次。
同键重试先核对参数；换新键是一个新业务操作。
本例首次超时后业务已经成功，展示的是不确定结果，不是服务端完全失败。
裸 `raise`在except中重新抛当前异常，保留失败语义与堆栈。
真实退避应加入抖动和总deadline，不应在async函数里使用time.sleep阻塞事件循环。
