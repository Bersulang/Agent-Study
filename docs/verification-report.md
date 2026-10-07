# 全课程验证报告

验证日期：2026-10-06。环境：Windows PowerShell、Python 3.12.10。

## 本轮材料复核：2026-10-07

从项目根目录执行`.\.venv\Scripts\python.exe tools/verify_course.py`，结果通过：56阶段、270个Python文件、225份Markdown、219条命令、172个标准库测试方法。该验证包含本轮课程材料静态检查及默认演示/练习/答案运行；通过只证明材料和机制测试可执行，不证明学员能力或外部服务集成。

阶段13共12项测试通过（原有3项，新增反馈循环9项）；动作列表示例、反馈循环示例、练习待完成骨架和独立反馈参考解法均已单独运行。阶段05/06的10个新增短示例逐个运行，均退出码0；统一验证器不会自动运行这些新增文件，因此手工执行结果单列记录。

本次手工验证命令（项目根目录，PowerShell）：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s lessons/13-agent-loop/tests -v
.\.venv\Scripts\python.exe lessons/13-agent-loop/examples/demo.py
.\.venv\Scripts\python.exe lessons/13-agent-loop/examples/feedback_loop.py
.\.venv\Scripts\python.exe lessons/13-agent-loop/exercises/feedback_practice.py
.\.venv\Scripts\python.exe lessons/13-agent-loop/solutions/feedback_solution.py

$python = '.\.venv\Scripts\python.exe'
$scripts = @(
  'lessons/05-types-objects/examples/01_class_composition.py',
  'lessons/05-types-objects/examples/02_types_dataclass.py',
  'lessons/05-types-objects/examples/03_comprehension_unpacking.py',
  'lessons/05-types-objects/examples/04_generators.py',
  'lessons/05-types-objects/examples/05_decorators.py',
  'lessons/06-async-testing/examples/01_sync_test.py',
  'lessons/06-async-testing/examples/02_await.py',
  'lessons/06-async-testing/examples/03_concurrency.py',
  'lessons/06-async-testing/examples/04_timeout_cancel.py',
  'lessons/06-async-testing/examples/05_async_test.py'
)
foreach ($script in $scripts) {
  & $python $script
  if ($LASTEXITCODE -ne 0) { throw "Failed: $script" }
}
```

本轮未调用付费/远程真实模型、真实Embedding、Spring Boot、Docker或目标生产身份服务。真实集成能力仍待验收；本轮结论不改变下方2026-10-06历史SDK状态。

## 验证方法

统一入口为`python tools/verify_course.py`：检查56阶段材料、教学源码编译、本地Markdown链接、默认演示、练习骨架、参考答案和标准库回归。机器可读结果写入忽略目录`artifacts/verification-report.json`。

默认案例与真实集成分开报告。练习骨架可以运行只代表材料可加载，所有学员能力仍待验收。

## 默认课程

最终完整运行已通过：56个阶段，256个Python文件，227份Markdown，219条运行与测试命令，163个标准库测试方法。源码语法、本地链接、默认演示、练习骨架和参考答案检查均通过。

重要回归覆盖参数校验、流式边界、权限、取消、共享状态冲突、协作预算、租约、审批、幂等、知识权限、恢复、发布门槛和路径边界。

## 真实集成

| 集成 | 版本与范围 | 实际结果 |
| --- | --- | --- |
| pypdf | 6.19.0，真实两页PDF夹具提取与空页识别 | 已通过 |
| LangGraph | 1.2.13，条件边、子图、Saver和中断批准/拒绝 | 已通过 |
| MCP stdio | 2.3.0，官方SDK客户端、工具/资源/提示与结构化输出 | 已通过 |
| MCP Streamable HTTP | 2.3.0，本机启动、发现、读取、关闭与断连 | 已通过 |
| A2A | a2a-sdk0.3.26，协议0.3，官方ClientFactory与本机HTTP | 已通过，不代表当前所有协议版本互通 |
| FastAPI | 0.115.12，TestClient业务、事件、隔离、取消；阶段39 | 已通过 |
| Java客户端探针 | Python→本机HTTP测试服务 | 已通过；不是Spring Boot联调 |
| OpenTelemetry | 1.45.0，真实SDK父子Span与内存导出 | 已通过，不连接OTLP后端 |
| Playwright | 1.63.0，真实Chromium、本地HTML与结果断言 | 已通过，不访问外部业务网站 |
| 毕业API | 实际FastAPI+SQLite、审批、重放、租户与输入校验 | 2个接口测试已通过 |
| 模型HTTP | 假Token、Mock契约及拒绝全部3xx | 已通过离线契约，未调用真实模型 |

阶段17/27/28/29的具体SDK命令及依赖快照见对应integrations/verification.md；阶段30—43的详细集成记录见 [验证记录](../lessons/30-routing-roles/verification.md)。

制作课程时另外实际执行了以下检查（当时的临时SDK环境已停用，重跑前需按对应课程准备依赖）：

```powershell
python lessons/46-observability/integrations/otel_demo.py
python lessons/55-browser-multimodal/integrations/browser_demo.py
& "$env:TEMP/agent-study-services-venv/Scripts/python.exe" lessons/56-capstone/integrations/test_api.py -v
```

当时安装了本课锁定的OpenTelemetry/Playwright，Chromium通过官方安装命令下载；临时API环境依赖与阶段39一致。环境目录均不提交。

## 审查中修复的边界

- 模型适配默认urllib重定向可能把认证头带到其它主机或HTTP；已先复现，再在跳转前拒绝全部3xx并回归。
- SQLite事务上下文不会关闭连接；备份/恢复用closing释放句柄，验证Windows清理。
- 不存在的备份源会被普通connect创建为空库；已改存在性检查和只读打开，恢复检查业务Schema并禁止覆盖已有目标。
- 参考答案补齐错误和边界案例；writer权限与可信审批分开；数据目录无效或不可写时在监听之前拒绝启动。
- 毕业项目补新知识/只读工具、模型计划Schema、参数修改后的重新审批和交付手册。

## 未验证环境

- 未调用付费或远程真实模型，未测真实模型准确率、账单与供应商限流。
- 未下载Embedding/图像/语音模型，未验证真实识别或转写质量。
- 本机缺JDK/Maven，未构建Spring Boot或运行Java测试，也未Python→Spring端到端联调。
- 本机缺Docker，未运行镜像、Compose、容器沙箱或重启持久卷演练。
- 未验证生产OAuth/JWT提供方、TLS、公网协议互操作、分布式队列、企业负载或外部业务副作用。

以上环境都有课程说明或集成文件，但未执行的项目不标为通过。课程完整交付不表示对任何企业场景作通用生产保证。
