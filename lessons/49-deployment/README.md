# 阶段 49：部署、配置与健康检查

[课程首页](../../README.md) · [完整路线](../../docs/roadmap.md) · [本课知识](knowledge.md)

## 1. 业务场景

服务启动不代表能接工单：数据库不可用时应停止接收新任务，普通进程探活仍可正常。我们先学习配置校验与不同健康状态，再提供实际容器文件。

## 2. 学习目标与前置知识

先完成前面的 Python、工具、状态和协作基础。本课重点是理解机制，能够修改并验证代码。遇到不理解的语法先查看本课语法说明，再回到基础阶段复习。

学习完成后，能独立完成下方新需求，说明失败条件，并用测试检验结果。材料准备完毕不表示已经通过能力验收。

## 3. 关键概念

### 1. 环境配置

代码和部署配置分开。端口、数据目录来自环境变量，密钥来自受控秘密系统。启动时检查非法值，不等到用户请求才失败；不把默认开发密码当生产配置。

### 2. 存活与就绪

Liveness说明进程是否还在运行；Readiness说明依赖和状态是否允许接流量。数据库故障使就绪失败，但不一定需要不停重启进程。与Java应用健康检查相同，需要区分用途。

### 3. 镜像与持久数据

镜像包含程序和运行环境，容器生命周期独立于数据卷。非root用户、最小构建上下文、排除凭证，并用持久卷保存任务数据。SQLite本课只用于小规模教学。

## 4. 操作演示

默认案例使用 Python 标准库，固定本地数据，无需网络和模型密钥。以下命令从项目根目录运行：

```powershell
.\.venv\Scripts\python.exe .\lessons\49-deployment\examples\demo.py
```

本机示例输出：

```text
配置端口： 8080
正常健康： {'live': {'status': 200}, 'ready': {'status': 200}}
依赖故障： {'live': {'status': 200}, 'ready': {'status': 503}}
启动校验： PORT超出合法范围
```

先预测结果，再运行；不要只看最后一行，观察成功和失败请求是怎样分流的。

## 5. 代码执行过程与新语法

读取环境值并验证端口范围；根据依赖状态构造存活和就绪结果；默认演示仅调用函数，不开启常驻服务。integrations中包含真实HTTP服务、Dockerfile和compose，可按命令启动并检查健康接口。

### 本课语法提示

`environ`是配置字典；int转换可能抛异常；Path表示目录；不要在导入模块时直接启动服务，入口放在main判断中。

函数的参数表示需要提供的信息，返回值表示结果。异常表示当前调用不能继续，不能简单吞掉所有异常；需要将失败类别传给上层处理。注释与讲义共同解释关键决策。

## 6. 常见错误与排查

| 症状 | 原因 | 排查与修复 |
| --- | --- | --- |
| 程序启动但不可用 | 只检查进程存在 | 增加依赖就绪检查 |
| 重启丢任务 | 数据库保存在容器临时文件系统 | 使用持久卷并验证恢复 |
| 构建把密钥带进去 | 构建上下文包括.env | 最小上下文与.dockerignore |

排查时保留输入类别、状态与错误码；涉及身份、密钥和业务数据时，先脱敏再记录。一次运行成功只能证明当前案例，必须覆盖变化后的需求和失败路径。

## 7. 独立练习

1. 增加数据目录配置并在启动时检查可写性，不输出敏感值。
2. 依赖故障时就绪返回503，存活返回200。
3. 用真实容器命令启动后记录重启前后数据是否保留；无Docker时说明未验证项。

编辑 [练习骨架](exercises/practice.py)。完成后运行自己的案例，再对照 [参考答案](solutions/solution.py)。答案只提供一种实现，你可以使用更清楚的结构，只要行为满足要求。

```powershell
.\.venv\Scripts\python.exe .\lessons\49-deployment\exercises\practice.py
.\.venv\Scripts\python.exe .\lessons\49-deployment\solutions\solution.py
```

## 8. 测试与能力验收

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s .\lessons\49-deployment\tests -v
```

测试针对真实教学函数的成功和失败行为。练习尚未完成时，参考实现测试通过不能证明你的实现也正确，你需要为新增需求编写案例。

解释存活与就绪差别；展示非法端口会启动失败；说明镜像、容器和卷的区别，不把本地函数验证称为容器通过。

提交你的代码、操作结果、错误排查记录和设计解释。验收至少检查：能解释机制、能完成新需求、能定位故障、能给出验证依据。

## 9. 企业工程边界

本机未发现Docker，因此默认行为实测，容器配置仅提供可执行文件和命令，运行验证留给有Docker的环境。生产基础镜像固定digest、漏洞扫描、权限和资源配置需按部署平台补充。

生产接入需要按场景明确身份、数据保留、故障恢复、容量和发布策略。本课程案例的验证范围是本地确定性行为，未调用真实外部模型或声称在生产环境通过。

## 10. 知识回顾与参考资料

复习 [本课知识文档](knowledge.md)，将实际遇到的问题写到练习记录，经分析后再同步知识手册。

- [Docker构建实践](https://docs.docker.com/build/building/best-practices/)。
- [Python HTTP服务](https://docs.python.org/3.12/library/http.server.html)。

## 源码分段追踪与Java对照

### 输入和初始化

load_config只解析PORT和DATA_DIR，不进行文件写入。

int转换端口失败说明配置非法，不能悄悄切回默认端口。

1到65535是本课允许范围，0不作为自动分配端口。

startup_config是启动门禁，真实server在绑定监听端口前调用。

默认DATA_DIR为artifacts/service-data，需先显式创建。

### 校验与状态推进

不存在的目录拒绝启动，避免拼错路径后生成意外数据树。

路径存在但实际是文件，抛NotADirectoryError，不尝试覆盖。

目录权限不能靠os.access可靠判断，尤其Windows ACL与只读属性不同。

TemporaryFile在指定目录真正创建文件，再写入和flush。

退出with关闭并删除探测文件，不在业务目录留下垃圾。

写入发生OSError后转换为PermissionError，启动停止且不暴露配置细节。

权限检查成功后仍可能在运行中失效，因此就绪探测继续检查依赖。

health(False)返回live200和ready503；进程活着但不接收业务流量。

### 失败与验证证据

真实服务用数据库查询探测就绪，连接由closing显式关闭。

ThreadingHTTPServer是本地教学HTTP服务，不是完整生产应用服务器。

Dockerfile非root运行，DATA_DIR配置为挂载的数据目录。

Compose命名卷保持重启数据，容器可写层不承担持久任务。

镜像同时包含server与同课demo，让启动门禁在容器内仍可导入。

Compose down不删除命名卷，down -v会删数据，不应用于保留数据演练。

本机未运行Docker；必须在有Docker环境记录实际重启与数据库数据结果。

### Java Web迁移

startup_config类似Spring启动时配置校验与ApplicationRunner探测依赖；配置绑定不代表目录可写。Java Files.createTempFile与Python TemporaryFile都需要真实写入测试，readiness与liveness也不能合并。

完整练习覆盖说明见[参考答案说明](solutions/README.md)，请在完成练习后阅读。
