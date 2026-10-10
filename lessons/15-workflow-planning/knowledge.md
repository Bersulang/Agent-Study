# 阶段15复习：流程依赖和有限重规划

关联：[讲义](README.md)、[演示](examples/demo.py)、[练习契约](exercises/README.md)。

## `state`、`plan`、`history`分别保存什么？

`state`表达当前终态或中间状态，`plan`列出未执行步骤，`history`保留已经发生的转移。已识别的“登录”请求先走`search → answer`；search完成后，completed集合记录它已发生。无证据时只把尚未执行的answer替换为human_review，历史中的retrieved不会消失。

## 子集检查怎样保护步骤顺序？

`DEPENDENCIES["answer"]`是`{"search"}`；执行answer前检查它是否为completed的子集。`<=`是集合子集运算，不是大小比较。若answer被错误地排到search前面，依赖检查会拒绝这个顺序，而不是让计划文字直接触发回答。

先预测：`max_replans=0`且search没有证据时会怎样？程序保留retrieved，不能再替换answer，进入stopped。预算为1时计划改成human_review，最终历史含replanned。未知问题在检索前进入clarify。

## 为什么重规划不能清空历史？

计划代表未来，历史代表过去。清空历史会让调用者看不见已经进行的搜索；若此前发生写操作，甚至可能造成重做副作用。本例只有只读搜索，但仍保留记录，示范了同一原则。重规划次数必须有限，否则空证据可能导致重复搜索。

## Java迁移与边界

可把依赖集合视作简化的BPM前置条件；Java常用`containsAll`表达同一检查。固定流程适用于已知业务步骤，不必引入Agent。演示中的证据布尔值是本地夹具，不是检索质量证明。完成[练习](exercises/README.md)时，保持权限检查、search依赖和有限query_rewrite顺序清晰。
