# 实际毕业API与交付演练

先运行本阶段离线流程并通过回归，再学习此真实FastAPI接口。它使用真实数据库和审批机制，但模型与身份仍为明确标注的教学夹具。

本目录的接口任务补充[毕业练习验收矩阵](../exercises/README.md)，共用一份项目交付标准。毕业交付还需用目标环境验证真实身份、流式任务事件、取消、持久队列、重启恢复、部署/回滚/恢复；此处的教学身份和确定性模型仍属于机制夹具。

安装与阶段39一致的依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r lessons/39-fastapi-service/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/56-capstone/integrations/test_api.py -v
.\.venv\Scripts\python.exe -m uvicorn app:factory --factory --app-dir lessons/56-capstone/integrations --host 127.0.0.1 --port 8090
```

第三条命令常驻，Ctrl+C停止，数据保存在忽略目录`artifacts/capstone`。只监听本机，不对外暴露教学会话Token。

查询API说明可打开`http://127.0.0.1:8090/docs`。调用示例：

```powershell
$headers = @{Authorization = "Bearer lab-a"}
$body = @{question = "创建工单:登录失败"; key = "request-001"} | ConvertTo-Json
$draft = Invoke-RestMethod http://127.0.0.1:8090/tasks -Method Post -Headers $headers -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
$approval = @{key = "request-001"; digest = $draft.digest} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8090/approvals -Method Post -Headers $headers -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($approval))
```

在60秒教学审批窗口内执行；过期应拒绝，而不是绕过校验。重复请求使用同一幂等键与参数，返回原工单。

## 独立毕业任务

1. 增加一个只读工单工具与新知识来源，明确定义Schema和权限。
2. 接真实模型适配，校验计划；保留离线模式便于自动化回归。
3. 替换教学身份为真正的认证验证和服务端授权，禁止接受客户端自报角色。
4. 增加流式任务事件、取消和持久队列；审批不可被模型自行批准。
5. 用阶段49—52方法形成发布、回滚、容量和恢复说明。

真实集成验收需要实际展示认证身份不能由客户端自报、取消/重连事件、持久任务跨进程恢复以及重复请求的幂等结果。缺少目标服务环境时保留“集成待验收”。

## 交付文档清单

需求与成功标准、架构与数据流、工具契约、权限矩阵、知识更新、评估集和报告、执行轨迹、版本包、部署、回滚、恢复和运维手册。

测试通过只覆盖本地接口和夹具，不代表真实模型、生产认证或企业负载通过。请填写自己的部署环境、目标负载、质量门槛、成本预算和未验证项。
