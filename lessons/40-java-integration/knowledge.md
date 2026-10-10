# 阶段40复习：跨语言错误与安全调用

关联：[讲义](README.md)、[离线契约](examples/demo.py)、[练习](exercises/README.md)、[Java集成](integrations/README.md)。

authorize_call先验证服务token，再比对租户与scope。身份不可信为401；身份已知但租户/scope不允许为403；通过后返回ticket和trace。JSON round-trip只验证基础数据契约。

练习将401、403、404、429/503及其他状态分类。429/503只对安全只读操作允许有限重试；写响应丢失可能已经提交。真实Java服务需使用认证后的principal而不是相信请求体tenant，并验证实际授权、超时、错误映射和日志脱敏。


## 进一步检查

JSON往返测试关注的是wire contract：tenant是字符串、scopes是数组、trace可往返，不依赖Python对象身份。401表示服务凭据无效；403表示授权条件不符，二者分别触发重新认证或拒绝访问。响应不应包含敏感工单正文或服务器堆栈。

练习对429/503标记retryable_read，是基于只读操作的重试策略；HTTP状态本身不能证明写请求未成功。Java端实际Spring身份、租户查询和错误映射要用服务测试验证；离线claims字典不是JWT验证器。