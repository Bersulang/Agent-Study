# 阶段31复习：委派与完成条件

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

主控以task id去重后再找role对应worker；重复knowledge只调用一次。深度到达max_depth时在调用前返回depth_exceeded。缺少worker或worker返回None时结果不算完成，missing从已计划任务与有效结果的差集得到。

先预测：两个计划任务中ticket结果缺失，能否只因knowledge成功就completed？不能。练习进一步标required：必需项缺失阻断完成，可选项缺失只警告。Java的主控服务也应依据任务契约检查结果，而非只统计调用成功数。


## 进一步检查

`seen`只记录已经处理过的逻辑任务ID；若两个不同角色意外复用同一个ID，第二个任务也会被去重，所以ID生成规则本身必须跨角色唯一。Worker缺失和Worker返回None都会令结果缺失，练习输出的missing/warnings应从原计划任务计算，不能只遍历成功结果。

可以手算`tasks=[knowledge, ticket, knowledge]`：主控调用两次，重复knowledge不调用；若ticket是required且未返回，则状态仍不完整。Java里常见Future集合也需要保留每个future与原task id的映射，否则异常和结果可能错配。