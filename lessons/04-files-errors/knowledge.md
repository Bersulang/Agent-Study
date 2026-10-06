# 阶段04知识整理：文件、JSON与异常边界

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 路径与编码

定义：Path表示文件路径；相对路径根据当前工作目录解释；UTF-8规定字符与字节互换。

使用：中文JSON明确encoding="utf-8"，不依赖Windows默认编码。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## JSON与校验

定义：JSON是数据交换格式，loads把文本解析成Python对象；语法正确不代表字段正确。

使用：{"id":7}可解析，但工单id要求字符串时应拒绝。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 异常与上下文管理

定义：异常将正常执行转向匹配的except；with在退出时释放资源。

使用：FileNotFoundError与JSONDecodeError不同，不能一律返回空列表。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 日志

定义：日志记录事件与定位信息；业务数据和密钥不应原样全部记录。

使用：本课返回具体错误，生产日志可记录文件标识与错误类别。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 执行与失败路径

标准库模块导入后，main创建临时目录与Path对象。

dumps返回JSON字符串，ensure_ascii=False保留中文显示；write_text写UTF-8。

json.load读取并解析，之后逐条检查字段；isinstance检查实际对象类型。

覆盖为损坏内容后第二次读取抛出JSONDecodeError，进入指定except。

离开with清理临时目录；没有把损坏文件恢复为空列表。

## Java迁移

Java try-with-resources对应with；Jackson反序列化也要业务校验。Python异常无需throws声明，异常契约必须通过函数说明与测试明确。

## 工程应用

直接覆盖文件可能在崩溃时截断数据。后续持久化阶段使用同目录临时文件、原子替换或数据库事务；读写路径也要限制在授权工作空间。

## 复习与验证

先解释概念，再完成[独立练习](exercises/README.md)。

保留真实运行记录；参考答案能运行不代表你已掌握。

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
