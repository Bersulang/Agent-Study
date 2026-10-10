# 阶段39复习：任务API与事件续读

关联：[讲义](README.md)、[领域演示](examples/demo.py)、[练习](exercises/README.md)、[FastAPI集成](integrations/README.md)。

create先验证session/prompt，验证失败时tasks保持0；成功后创建running任务和progress事件。advance只接受running并追加text/final；cancel把任务转canceled，之后不能再追加final。`read`复制events列表，防止调用方篡改内部状态。

SSE续读参数after应解释为已收到的最后序号，只返回其后的事件；负数拒绝、session不符403。离线领域机制和真实HTTP/事件流是不同关卡，不能由材料或统一验证器代替学员验收。


## 进一步检查

当前demo只提供TaskService领域对象。真实API需把请求体校验映射为HTTP错误，将session身份从可信认证上下文取得，并为事件分配稳定递增序号。`after`是客户端确认已收到的最后序号，续读应严格筛选更大序号；重复返回已读事件会造成重复显示，跳号则会丢事件。

取消只能在任务仍running时成功。若服务端和Worker分离，取消还要传播到队列并定义已提交副作用的边界。实际FastAPI/TestClient/SSE验证记录在integrations；离线`TaskService`通过并不等于HTTP集成已通过。