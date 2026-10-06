# 阶段10知识整理：结构化输出、SSE与取消

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## JSON Schema与运行时校验

定义：Schema描述对象字段、类型与约束；结构化输出能力支持范围依供应商而变。

使用：title必填非空，priority整数1—5，additionalProperties=false拒绝额外字段；仍需业务验证。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 网络块与SSE事件

定义：网络read返回字节块，边界任意；SSE按UTF-8文本行解析，用空行提交事件。

使用：一个事件可横跨多个字节块；中文可在多字节中间切开，必须增量解码。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## data行与完成标记

定义：多个data行以换行连接；注释心跳不产生业务数据；EOF不自动提交未终止事件。

使用：[DONE]是本课Chat风格应用标记，不是SSE规范通用字段，Responses事件另有结构。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 取消与提交边界

定义：取消使生成停止；只有完整完成并校验后才能发布草稿。

使用：先展示临时文本，最终返回对象；取消或缺少完成标记丢弃未提交草稿。

核查：在演示中找出对应位置，修改输入并预测结果。

边界：不要把本课的最小例子直接当生产实现。

## 执行与失败路径

UTF-8增量解码器保留尚未完整的多字节字符；buffer保留跨块文本行。

扫描CR与LF，CRLF视为一个换行；末尾CR等待后续块，注释行跳过。

空行提交data列表；同一事件多行data用换行连接，不能逐read调用json.loads。

collect_draft拼接不同delta事件，等[DONE]；取消会抛出专门异常。

json.loads后validate_draft执行类型和字段校验；返回的只是草稿，写入另需审批。

## Java迁移

可类比Java InputStreamReader处理字节到字符，BufferedReader.readLine处理行；read(byte[])不能当消息边界。Python生成器以yield交付事件，消费者可以在完成后停止读取。

## 工程应用

本课实现SSE数据字段与事件边界，未实现id重连、retry和命名事件分发；不是完整EventSource客户端。生产要处理连接超时、断连、流量上限与供应商事件JSON envelope。

## 复习与验证

先解释概念，再完成[独立练习](exercises/README.md)。

保留真实运行记录；参考答案能运行不代表你已掌握。

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
