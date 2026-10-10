# 阶段04知识整理：文件、JSON与异常边界

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 相对路径是相对于哪里？

`Path("tickets.json")`相对于当前工作目录，不自动相对于源码文件。演示显式把文件放进`TemporaryDirectory`返回的路径，因此不依赖你从哪个终端启动项目；查看PowerShell当前目录可用`Get-Location`。文本读写两端都指定UTF-8，防止中文行为跟着Windows默认编码变化。

## 解析成功等于数据正确吗？

不等于。`json.load`负责把JSON文本转成Python的list、dict、str、int等值；`load_tickets`还要验证顶层是list、每条是dict且`id`为字符串。`{"id": 7}`语法完全有效，但ID类型不满足工单契约，所以由字段校验抛`ValueError`。损坏JSON在解析阶段抛`JSONDecodeError`，甚至还没机会检查字段。

## 哪一层应该捕获异常？

资源层用`with`保证文件句柄关闭；解析层保留`JSONDecodeError`；业务校验层用`ValueError`指出数据不合格。上层只捕获自己能处理的异常。本演示捕获损坏JSON只为显示清楚的失败提示，没有返回空列表，因为空列表会掩盖数据故障。不存在文件、编码不匹配和字段错误也应分别诊断。

## 日志应该写什么？

`logging_demo.py`记录事件、文件标识和错误类别，不写工单正文。日志帮助运维定位；异常/返回结果通知程序调用者。若把两者混为一谈，可能既暴露隐私，又让业务调用方不知道操作失败。

## 执行与失败路径

状态追踪：临时目录中先写入`[{"id":"T1","title":"无法登录"}]`，读取后得到list并通过字段检查；随后同一路径内容改为`{broken`，解析阶段立即失败，捕获分支输出损坏提示。文件句柄在异常后关闭，临时目录最终删除；数据没有被替换成“空工单”。

## Java迁移

Java `try-with-resources`对应`with`；Jackson反序列化与Python JSON解析都只负责结构转换，业务层仍须检查不变量。Python不强制throws声明，因此需要在文档和测试里明确可能失败的情况。

## 工程应用

直接覆盖文件可能在崩溃时截断数据。后续持久化阶段会用同目录临时文件、原子替换或数据库事务；文件路径也要限制在授权工作空间。练习的输入是JSON文本，要求统计前先验证列表、非空ID和重复ID，详见[练习契约](exercises/README.md)。

## 复习与验证

先预测`{"id":7}`失败在解析还是字段校验，再预测`{broken`会走到哪一步；随后完成[独立练习](exercises/README.md)，至少区分语法损坏、ID重复和合法空列表。参考答案能运行不代表你已掌握。

[官方来源](https://docs.python.org/zh-cn/3.12/library/json.html)

## 日志补充演示

从根目录执行 `python lessons/04-files-errors/examples/logging_demo.py`，实际输出：

```text
WARNING ticket_import event=load_failed file_id=teaching-fixture error=json_corrupted
```

[日志源码](examples/logging_demo.py)在入口配置命名logger；不在模块导入时改全局配置。
`StreamHandler`决定日志去向，`Formatter`决定显示格式，`setLevel`决定最低记录级别。
DEBUG用于细节诊断，INFO用于正常事件，WARNING用于可处理异常，ERROR用于失败。
`logger.warning`记录开发者事件；它不会代替给业务调用者返回失败。
这里不记录整个工单或异常正文，避免业务资料进入无控制的日志。
`finally`无论成功还是异常都执行，用于清理；`with`通常能表达同样的资源生命周期。
`raise ValueError(...)`主动拒绝无效数据，`except ... as error`把异常对象绑定到名称。
[Python日志官方资料](https://docs.python.org/zh-cn/3.12/library/logging.html)。
