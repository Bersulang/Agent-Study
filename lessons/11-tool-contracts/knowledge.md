# 阶段11知识整理：工具契约与参数校验

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 工具描述是权限吗？

不是。描述只帮助模型选择`ticket_lookup`；Python的`TOOLS`注册表决定哪些调用真的存在。模型请求未注册的`exec`时，`dispatch`返回unknown_tool，而不是执行它。生产系统还要从可信登录上下文读取调用者身份并检查对目标工单的权限，本课没有身份系统。

## Schema存在后还要本地校验吗？

要。`TOOL_SPEC`只描述对象需要一个字符串id且拒绝额外字段；Python函数可能从测试、脚本或其他调用方直接被调用。演示还运行时检查dict类型、`set(arguments) == {"id"}`、非空字符串，随后才查数据。`{"id":"T1","admin":true}`必须因多余字段失败；Schema不拦截所有本地调用。

## 为什么用结果信封？

成功信封有`ok=True`、`data`副本、`error=None`；失败信封有`ok=False`、`data=None`、稳定code和`retryable=False`。参数类型错误用invalid_arguments；合法但不存在的ID用not_found；工具名不在注册表用unknown_tool。类别分开后，上层能决定澄清、回退或终止，不必解析错误文案。

## 为什么返回副本？

`ticket_lookup`对命中的T1执行`.copy()`再放进data。若把共享的`TICKETS["T1"]`原字典交给调用者，调用者修改结果也会改写演示数据；副本避免这种意外共享。本例只复制一层，因为数据当前只有字符串字段。

## 执行与失败路径

调用顺序是`dispatch -> TOOLS查表 -> ticket_lookup校验 -> TICKETS查找 -> 结果信封`。当name=exec时在查表处终止；当id=1时在参数校验处终止；当id=T9时才进入数据查询并返回not_found；id=T1则成功返回副本。

## Java迁移

Java DTO校验与路由白名单对应参数验证和TOOLS注册表。Python函数可直接作为字典值调用；两种语言都不能把模型提供的参数当成已经认证的用户身份。

## 工程应用

查询与写入工具分开，写入需要审批与幂等。输出限制字段和大小，避免大量敏感数据进入模型上下文；真实身份由服务器注入而不是模型参数指定。

## 复习与验证

练习见[独立练习](exercises/README.md)：为status检索增加明确参数域和不同错误码。先列出未知工具、未知status和成功列表各自预期信封，再实现；真实用户身份仍需下一层服务提供。

[官方来源](https://json-schema.org/understanding-json-schema/reference/object)

## 契约和身份的两个边界

模型生成的name/args均不可信；查表限制能力，字段校验限制调用形状。
调用者身份不能放在可由模型任意填写的args中，真实服务应从已认证上下文传入。
工具description帮助选择，但不能绕过执行器校验。
`set(arguments) != {"id"}`要求字段集合恰好相同；{}是字典，{"id"}是只有一个元素的集合。
