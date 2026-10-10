# 阶段 55 独立练习

1. 页面重复提交返回同一工单ID；未审批提交失败。
2. 拒绝未知MIME、空文件与超大文件，不能只根据扩展名信任内容。
3. 完成真实本地页面脚本；有本地模型时测试一张图片或一段语音，记录识别错误和验证范围。

## 提交

提交练习代码；自动校验命令会保存运行结果。设计原因可在验收对话中说明。

## 验收

区分离线页面状态机与实际浏览器；提交后验证真实结果；解释多模态理解的不确定性和凭证保护。

完成后查看 [参考答案](../solutions/solution.py)，不要预先复制。

## 自动校验接口

实现`solve(data)`，契约如下：

`data`必填`key`、`mime`、`content`和`approved`；`max_chars`可选（默认4096）。允许的MIME为`text/plain`、`text/markdown`、`application/pdf`。返回`accepted`、`ticket_id`、`replayed`；未审批、MIME不允许、空内容或内容长度超过max_chars时拒绝，ticket_id为None且replayed为false。同一运行内同key同内容重放复用编号并标记replayed为true；同key不同内容拒绝。真实浏览器与模型集成不由此测试证明。

自动校验只验证上述可重复的行为子集；涉及真实模型、服务、身份、部署或需要设计解释的部分，仍按本课集成任务独立验收。校验日志由统一命令自动保存，不要求手工粘贴命令输出。

从项目根目录运行：`.\.venv\Scripts\python.exe tools/check_exercise.py 55`。
