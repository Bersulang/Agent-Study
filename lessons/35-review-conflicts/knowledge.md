# 阶段35复习：核对主张和证据

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习](exercises/README.md)。

review先比较证据value集合；不止一个值就返回conflicting_evidence。值唯一后，draft.value必须匹配，draft.citation也必须属于证据ID。revise最多做有限轮数；从一条证据复制值不能解决两个有效来源的冲突。

先预测：引用存在但数值不同，能accepted吗？不能，主张仍unsupported。练习按active和authority筛证据；先取最高级，再检查同级冲突，不能依赖列表顺序。政策权威和生效时间必须由业务规则确定，不能由模型自行偏好。


## 进一步检查

`review`中值集合长度为0也属于不通过：没有证据不能让任意主张成立。只有一项证据时citation仍需指向该项；值正确但引用来自未检索材料也拒绝。`revise`用固定修订轮数避免自动修正无限循环，但示例修订策略并非生成模型或真实审核器。

练习的authority先决定候选，再比较最高层是否冲突；较旧但权威的政策是否有效，需要输入的active/effective字段说明。Java实现也应把验证结果做成结构化类型，区分conflict、unsupported_claim和no_evidence供人工处理。