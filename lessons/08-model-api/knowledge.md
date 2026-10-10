# 阶段08知识整理：模型API、上下文与成本

关联课程：[讲义](README.md)；例子：[可运行演示](examples/demo.py)。

## 中文字符数能当token数吗？

不能。token是模型编码单位，中文字符与token没有固定一对一关系；上下文窗口还要同时容纳系统规则、历史、检索内容与模型输出。Mock的20输入、10输出token是硬编码测试数据，只为演示计费，不是对问题文本的真实分词。

## 消息角色在哪里起作用？

`messages`是有序的角色/内容字典列表。本课先放system规则，再放user问题；`MockModel.complete`取最后一项的`content`并拼出模拟文本。不同API对system、developer、tool及内容块的支持不同，适配器需要按供应商契约翻译。角色分隔有助表达指令层次，但不能代替鉴权或隔离不可信数据。

## HTTP 200表示回答正确吗？

不表示。HTTP成功只代表请求响应层面正常；模型可能拒答、返回非预期格式、缺usage或给出错误事实。适配器统一请求格式、认证、异常映射与字段转换，业务层再评估答案。此项目真实HTTP适配是文本接口，不实现原生工具调用内容块，不能用它冒称阶段13真实Agent闭环。

## 成本公式中的价格是谁给的？

演示按`(20*1 + 10*2)/1_000_000`得到0.000040，费率1/2只是调用者提供的教学数字。真实账单必须依据特定模型、版本、生效时间及usage；没有usage时应记录未知，不能记0。

## 执行与失败路径

正常轨迹：system/user消息进入本地Mock，最后一项问题被拼入text；固定usage作为结果字段返回；成本函数把用量和费率按百万单位换算。改变费率只改变成本，改变问题只改变mock文本。真实HTTP请求仅通过integration显式运行，可能计费。

## Java迁移

可类比Java接口/SPI：上层仅依赖统一`complete(messages)`，供应商响应字段由适配器转换。Python鸭子类型允许Mock与真实实现只要提供相同行为即可替换。

## 工程应用

后续把重试、超时、模型路由和费用追踪放在统一边界。保留模型版本、请求ID和usage，再区分接口可用性、任务正确率与安全性；unknown usage不能记零成本。

## 复习与验证

先预测提高output_rate时成本变化多少，再完成[独立练习](exercises/README.md)，实现用量非负校验与预算allow/deny。不要调用真实模型；练习考的是预算边界，不是模型答案质量。

[官方来源](https://developers.openai.com/api/reference/resources/chat)

## 真实接口与模拟接口怎么切换

业务依赖 `model.complete(messages)`，模拟与HTTP适配实现相同方法名和内部返回结构。
这里统一的usage字段允许None，表示供应商未报告；未知用量不能按0计费。
真实HTTP响应的prompt_tokens/completion_tokens由适配器转换为内部input_tokens/output_tokens。
不要在业务层散布供应商JSON路径，也不要为了兼容把拒答吞成空字符串。
不同API的工具调用、消息角色、流事件与参数支持不同，先核查再增加显式适配。

## HTTPS与重定向是两层边界

HTTPS保护当前连接；重定向决定下一次连接的目标，不能只检查初始地址。
本项目Python 3.12.10默认处理POST的部分301/302/303时复制Authorization，允许HTTPS或HTTP目标。
跨源可能把密钥交给其他服务器，降级可能转成明文传输。
本课[真实HTTP适配](integrations/http_model.py)使用私有build_opener，替换HTTPErrorProcessor。
收到任何300—399响应立即关闭并抛ModelAPIError，不创建下一请求；包含307/308和同源跳转。
`https_response = http_response`表示两个处理入口使用同一个函数实现，不是再次调用函数。
`super().http_response(...)`把非3xx交给基类正常处理，保留原HTTP成功与错误逻辑。
不使用install_opener，避免一次模型调用修改应用其他模块的全局HTTP行为。
错误中不包含Token、Location或正文；地址配置需确认供应商的最终HTTPS端点。

验证：新增测试先在旧实现失败，再修改策略；8个测试方法通过，枚举300—399全部状态码。
重定向测试只替换最终HTTP/HTTPS传输，保留真实urllib处理链，并断言仅有一次模拟请求。
测试仅用fake-token与example.test，未触网、未请求真实模型；Mock不能证明真实账号连通。
[官方处理链资料](https://docs.python.org/3.12/library/urllib.request.html)。
