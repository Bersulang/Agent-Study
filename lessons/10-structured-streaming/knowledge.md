# 阶段10知识整理：结构化输出、SSE与取消

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 一块read结果等于一个事件吗？

不等于。网络块任意切分，可能只包含一段`data:`行，也可能把一个UTF-8字符拆开。增量decoder保留不完整字节，文本buffer保留未结束的行；只有SSE空行边界才提交事件。CRLF也要作为一个换行处理。

## JSON解析应放在何时？

不要对每个网络chunk直接`json.loads`，chunk不是JSON边界。先按SSE规则把一个事件的data行拼起来，再按应用协议处理内容。本课wire直接把JSON文本分在多个data事件中，`collect_draft`累计后再拼接；真实Chat流可能先要解析SSE中的JSON envelope，再取delta文本。

## [DONE]属于SSE规范吗？EOF会结束草稿吗？

`[DONE]`是本课演示的Chat风格应用完成标记，不是SSE规范字段。parser遇到空行才yield事件；传输EOF不会替缺少的事件空行或完成标记补数据。没有[DONE]时，`collect_draft`拒绝返回对象。

## Schema通过就能写入系统吗？

不能。`validate_draft`只确认值是包含title和priority的精确dict，title非空且priority是1—5严格整数。草稿通过结构校验后也还不是已获权限的工单；提交需走服务端权限与审批。取消或断流时临时字符串不会变成正式业务状态。

## 执行与失败路径

每3字节输入后，decoder先补齐字符、buffer再补齐行；空行将data行交给`collect_draft`。草稿片段暂存在局部parts，随后收到[DONE]才解析完整JSON。移除[DONE]会保持done=False并拒绝；取消检查为真会抛StreamCancelled。Schema通过返回的只是草稿对象，不会触发写入。

## Java迁移

Java `InputStreamReader`和`BufferedReader`也分别处理字节解码与行边界；读取块不是协议消息。Python生成器可以每个完整SSE事件yield一次，消费者再累计应用层需要的字段。

## 工程应用

本课实现SSE数据字段与事件边界，未实现id重连、retry和命名事件分发；不是完整EventSource客户端。生产还需连接超时、断连、流量上限与供应商事件JSON envelope。

## 复习与验证

练习入口见[独立练习](exercises/README.md)：保留title/priority契约，新增可选description并限制累计字节数。先预测未完成流是否返回草稿，再实现超限与非法字段拒绝；不自动“修好”模型数据。

[官方来源](https://html.spec.whatwg.org/multipage/server-sent-events.html)

## Schema、修复与流事件再区分

[草稿Schema](examples/draft.schema.json)记录结构约束；JSON不支持注释，文件说明在本讲义。
`minLength: 1`允许空白字符串，本课运行时额外用strip拒绝只包含空格的标题。
`set(value)`得到字典键集合，精确相等拒绝额外字段；不是比较所有字段值。
`partition(":")`分割为字段名、分隔符、剩余内容，避免把data中后续冒号切碎。
`lambda: False`返回默认取消状态，调用者可传函数读取自己的取消令牌。
生产Chat流通常发送包含choices/delta的JSON，先从SSE解析事件，再解析供应商envelope，最后累计content。
字段修复必须有限次数且记录错误；本课故意拒绝非法对象，不把自动补全当可靠事实。
缺少结束标记属于未完成，本课不会自动重试生成。取消后既不提交草稿也不执行工具。
