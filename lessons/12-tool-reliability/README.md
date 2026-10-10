# 阶段 12：重试、幂等与不确定结果

## 使用场景

创建工单已成功，但网络响应丢了。直接重试可能产生第二张工单。用幂等键把逻辑操作和多次传输区分，并只对可重试错误做有限重试。

本阶段主线是企业知识与工单助手。默认演示只使用标准库和本地固定数据。
它用于理解工程机制，模拟响应不能证明真实模型质量或生产系统可靠性。

## 学习目标

- 能按错误类别决定是否重试，并设定最大总调用次数。
- 能解释超时后的未知结果，并使用同一个幂等键和相同参数查询/重放操作。
- 能证明同键不同参数拒绝、权限失败不触发写入，且不同键允许相同标题。
- 能指出内存幂等记录在进程重启和多实例下的限制。

## 前置知识与阅读顺序

先完成阶段 11 的讲解与验收；课程材料可以预先阅读，能力状态仍待验收。
需要能从项目根目录执行 Python 3.12 脚本，理解此前介绍的变量和函数。
如果新语法不熟，先读下面的概念与执行过程，再运行演示。
本课无需安装第三方包；不要为运行演示填写模型密钥。

## 关键概念

本课首次讨论写工具的重试与幂等。从第一项写操作开始，验收就要包含服务端权限、审批绑定的动作和参数、重复提交以及响应不确定场景；写工具不能仅凭模型提出动作直接执行。

### 1. 瞬态错误与永久错误

超时或短暂连接故障有时可重试；参数错误和权限错误重复同一请求不会变好。demo只捕获`TimeoutError`；`ValueError`和`PermissionError`直接向调用者传播。有限次数避免无限消耗时间和成本，`attempts=2`表示总共最多调用两次，包含第一次。

下面是机制相关的代码片段，需在原文件的函数或循环上下文中阅读，不是独立运行脚本。

```python
for attempt in range(attempts):
    try:
        return store.create(key, title)
    except TimeoutError:
        if attempt == attempts - 1:
            raise
```

最后一次仍超时就裸`raise`保留当前异常；不应该把所有异常都重试，也不要在async服务里用`time.sleep`阻塞事件循环。

Java对照：try/catch只控制重试流程；它本身不能提供Exactly Once。错误是否可重试是业务/协议契约。

### 2. 幂等键与参数绑定

幂等键标识同一个逻辑操作，而不是标题或用户。Store首次收到request-1时创建T1并保存`request-1 -> (title, result)`，随后模拟响应丢失。重放同键同标题会返回同一T1；若同键改了标题，则拒绝，避免把另一个操作冒充重试。

```python
old_title, result = self.requests[key]
if old_title != title:
    raise ValueError("同一幂等键不能绑定不同参数")
return result.copy()
```

不同键但相同标题可以代表两次真实的业务请求，所以练习明确允许它们创建两个工单。

<details><summary>先预测：第二次请求换成request-2但标题仍是“登录失败”，会复用T1吗？</summary>

不会。新键代表新逻辑操作，会创建另一张工单。把标题当键会错误合并两位客户的相同请求。
</details>

### 3. 超时与未知结果

`TimeoutError`只说明调用方没有按时收到返回。示例Store已经写入工单和幂等记录，才故意抛出TimeoutError。因此马上换新键会重复写；正确重试应沿用原键和相同参数，或先查询服务端记录。客户端取消请求也不能证明远端事务回滚。

离线内存字典只能展示语义：进程退出后记录消失，两个进程也可能同时查不到键并各自写入。生产需持久化唯一约束，并让幂等记录和业务副作用在同一事务中提交。

### 4. 权限、大小与凭证

`retry_create`在写入前先检查allowed，再校验attempts、key和title。allowed只是离线教学开关；生产授权要读取可信身份和策略，模型不能传`allowed=True`给服务端获得权限。键要求非空字符串，attempts必须严格为1—3整数，标题为非空文本且长度不超过100；拒绝发生时Store不应收到调用。认证凭证也不能放进模型消息或日志。

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

起始状态是`tickets=[]`、`requests={}`。`retry_create`先看allowed，然后检查2次尝试、非空request-1和标题“登录失败”。第一次`Store.create`新增T1，同时写入两份内存记录后抛TimeoutError；循环第二次仍传同一个key/title，命中requests并返回T1副本。最终`tickets`长度为1。随后用request-1和新标题调用时，找到旧记录但参数不同，抛ValueError，不进入TimeoutError重试分支。

失败反例：如果异常后换成request-2重试，Store看见新操作并可能创建T2；如果对ValueError也重试，问题仍然存在且调用被无意义重复。

## Java 对照

Java服务同样要靠数据库唯一约束和事务维持幂等；try/catch并不等于恰好一次。Python内存字典仅演示逻辑，进程重启、多线程和多实例均不保证原子性。

## 易错点与排查

- 重试换新键：服务端视为新操作，可能重复写入。
- 所有异常重试：权限错误不应反复调用。
- 超时认为没写：超时可能发生在写入之后。
- 无限重试：消耗预算且阻塞任务；真实系统采用有限次数、退避、抖动与总期限。

排查顺序：先核对错误类别和当前attempt；然后查看Store是否已产生副作用以及幂等记录；最后确认重试沿用原键/参数，权限或参数错误没有进入重试循环。
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

1. 同键同参数重放只产生一张工单；同键不同参数拒绝；不同键同标题会创建两张。
2. 证明权限拒绝、非法attempts、空key和无效title都发生在Store写入前。
3. 解释首次写入成功但响应超时后为何结果未知，及重试为何必须保留原key与参数。
4. 说明内存Store不能证明重启恢复、跨进程原子性或生产Exactly Once。
5. 自动校验保存离线行为结果；持久化一致性和并发竞争另需集成验收。

## 企业工程延伸

本课幂等存储只在单进程内有效。生产使用持久化唯一约束、参数摘要、操作状态与结果记录；幂等写入与业务写入必须事务一致，恢复阶段再处理未知结果。

本课Store只用单进程内存，重启后幂等记录丢失。生产要把幂等键、参数摘要、操作状态和结果持久化，并通过数据库约束和事务保证写入一致；未知结果还需可查询和可恢复。

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


## 自动练习校验

从项目根目录运行`.\.venv\Scripts\python.exe tools/check_exercise.py 12`，校验结果与日志自动保存；课程能力和真实集成仍按本课原有标准验收。
