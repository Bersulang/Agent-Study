# 阶段28复习：把本地工具契约映射到MCP概念

关联：[讲义](README.md)、[dispatch演示](examples/demo.py)、[练习契约](exercises/README.md)。

演示先查看method：`tools/list`返回get_ticket说明；`tools/call`再解析`params.name`与arguments中的ticket_id。未知method、未知工具和空ticket_id是不同失败点，练习将它们转换为不同错误码，且不暴露异常堆栈。

Tool是可调用操作，Resource是供读取的数据，Prompt是可复用消息模板；它们有不同输入输出契约。工具列表中声明required参数也不代替运行时校验。服务端仍要验证调用者身份和工单访问权。

先预测：将method设成`tools/call`但name写错，会回什么？拒绝未知工具，不会返回“工单不存在”。本demo只模拟dispatch字典，不实现MCP初始化、JSON-RPC传输或stdio生命周期。真实SDK需要连接与能力协商；stdio中stdout只能承载协议消息，调试输出写stderr。
