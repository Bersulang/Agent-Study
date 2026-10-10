# 阶段37复习：远程Task生命周期

关联：[讲义](README.md)、[离线Registry](examples/demo.py)、[练习](exercises/README.md)、[A2A集成](integrations/README.md)。

submit建立submitted；finish只有submitted才写artifact并转completed；cancel将未完成任务转canceled。取消后再次finish无产物，completed取消应拒绝且保留产物。未知任务查询返回task_not_found。

Agent Card说明能力，不代表授权；Task和Artifact是协议对象。当前Registry是离线教具，真实A2A需通过SDK、服务发现和任务协议验证。取消响应也不能证明对端业务副作用已回滚。


## 进一步检查

离线状态轨迹是submitted→working→completed；取消路径为submitted→canceled，finish看到非submitted就返回，artifact仍为None。重复task id在submit阶段拒绝，未知get则返回明确error。`cancel_terminal`练习要把不存在任务、终态任务和可取消任务区分开，不应为了统一接口而删除已完成产物。

真实A2A将状态消息与任务产物作为协议对象，不是自定义HTTP接口加一个Agent名字。运行集成时要记录SDK/服务地址、任务ID、状态事件和认证边界；没有真实服务只能记录离线机制，不能标集成已通过。