# 阶段29复习：重试次数和远程工具兼容

关联：[讲义](README.md)、[离线演示](examples/demo.py)、[练习契约](exercises/README.md)、[真实集成说明](integrations/README.md)。

`attempts=2`表示总共最多两次调用。第一次ConnectionError后再试一次；成功则立即return。最后一次仍断连时转成RemoteError。代码只捕获ConnectionError，因此PermissionError不会被误判为网络问题，也不会重复认证失败。

`compatible(required, discovered)`验证服务重新发现后仍提供所需工具。名称相同并不保证输入格式相同；练习把Schema版本也纳入兼容判断。新会话应重新发现能力，不能沿用断线前可能陈旧的清单。

先预测：写请求已在服务器完成，但响应断连，能否用call_read原样重试？不能。第二次可能产生重复写入。读请求通常可有限重试；写请求要使用幂等键、查询已提交结果或人工恢复。内存演示不实现Streamable HTTP、OAuth或真实远端认证；参考[集成说明](integrations/README.md)独立验收。
