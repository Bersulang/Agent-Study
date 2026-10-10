# 阶段42独立练习

## 业务需求

只有当前owner/token且租约尚未过期才可续租；过期拒绝；新Worker接管后旧token不能续租。

在`practice.py`实现`renew(queue, job_id, owner, token, now, ttl)`。允许调用同阶段demo已有接口，但核心新增规则由你实现。

## 输入与输出

输入沿用讲义中的对象/字典/任务id；参数名见函数骨架。
输出必须明确成功、拒绝或缺失状态，不用自然语言文本猜测流程状态。
不要改变调用方传入的列表/字典，除非函数职责明确是写状态。
涉及持久连接时用try/finally显式关闭，不能只依赖连接上下文。

## 必做场景

1. 一个满足全部条件的正常输入。
2. 一个字段缺失、结果缺失或没有符合条件对象的输入。
3. 一个不允许的状态变化、身份或版本。
4. 一个边界值：空集合、预算0、刚好过期、已读最后序号等，选择与你的函数相关的一项。
5. 证明失败前后不应改变的状态保持不变；有副作用时记录其数量。

## 工作方式

先在纸上给每个案例写期望结果，再实现函数并运行。
从项目根目录执行`python lessons/42-workers-queues/exercises/practice.py`。
骨架默认只提示任务；出现NotImplementedError表示你调用了尚未完成的函数。
完成实现后添加自己的调用与assert，使文件能有限退出。

## 验收提问

- 哪个条件保证失败输入没有继续触发下一步？
- 哪个数据代表事实，哪个是控制状态，哪个只是教学计数？
- 删除一个关键条件后，你的哪条验证会发现错误？
- 这段代码迁移到真实服务时，哪个边界需要额外验证？

提交练习代码；命令和结果由自动校验保存。用自己的话解释一个失败路径作为理解验收。
完成后再阅读[参考答案](../solutions/solution.py)，对照设计取舍，而不是只比变量名。


## 自动练习校验

从项目根目录运行：`.\.venv\Scripts\python.exe tools/check_exercise.py 42`。校验日志自动保存，无需手工粘贴命令输出。自动检查未覆盖的真实集成仍需按本课项目标准验收。


## 自动校验接口

实现`renew(queue, job_id, owner, token, now, ttl)`。接口契约：queue为examples/demo.py的SQLite Queue fixture；只有当前owner/token且now早于expires的leased任务续租成功，返回bool；过期或旧token返回False，ttl非正抛ValueError。

自动检查调用的是学生练习函数，示例只提供离线数据/领域对象fixture，不代表真实外部服务或学员集成已经通过。命令与案例输出自动保存，无需手工粘贴。

从项目根目录运行：`.\.venv\Scripts\python.exe tools/check_exercise.py 42`。
