# 真实FastAPI任务接口

这里是实际ASGI应用，版本固定为FastAPI0.115.12、Pydantic2.13.5、Starlette0.46.2、httpx0.28.1。`examples/demo.py`领域层仍只使用标准库，HTTP层才引入依赖。

## 根目录运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/39-fastapi-service/integrations/requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s lessons/39-fastapi-service/integrations -p test_app.py
.\.venv\Scripts\python.exe lessons/39-fastapi-service/integrations/app.py
```

已有虚拟环境时跳过第一条。`pip -r`读取固定依赖；安装联网，测试无需模型与外网。

服务启动后打开`http://127.0.0.1:8000/`，创建任务，再选择推进、取消或读取事件。`/docs`是FastAPI自动生成的交互文档。按Ctrl+C停止服务。

## 请求与事件

| 请求 | 用途 | 关键结果 |
| --- | --- | --- |
| POST /tasks | 传session_id和prompt创建任务 | 201及task_id |
| GET /tasks/{id} | 携带X-Session-Id查状态 | 状态和事件列表 |
| POST /tasks/{id}/advance | 手工模拟一次Worker完成 | completed或保持canceled |
| DELETE /tasks/{id} | 请求取消运行任务 | canceled，终态重复取消409 |
| GET /tasks/{id}/events?after=1 | 续读序号1之后的事件 | 有限SSE流 |

空或纯空白prompt返回422；不存在/不属于本会话的task返回404，避免透露其他会话任务是否存在。session头只是教学隔离线索，生产要从已验证的用户身份获取owner。

事件有序号、类型和数据：progress描述进度，text描述内容，final描述完成，canceled描述取消。SSE每个帧以空行结束，`id`是重连游标。浏览器页面用fetch读取有限事件快照，再记录最后id；不是永远挂起的实时订阅。

## 逐层解释

`@app.post`装饰器在模块导入时注册路径，类比Spring@RequestMapping。`CreateTask(BaseModel)`定义请求对象，Field限制长度；`@field_validator`拒绝纯空白。普通Python函数注解本身不会执行这些校验，Pydantic框架读取后才会校验。

`owned`先做领域归属验证，再调用TaskService。取消改变状态为canceled，`advance`只能处理running，因此取消后不可能再追加final。

`stream()`是带yield的生成器；StreamingResponse逐步消费它并写响应体。教学流只读事件快照，会有限结束；真实长任务需要持久事件、心跳、取消感知和背压。

HTML页面用textContent显示返回文本，避免把返回内容解释为HTML。这里无模型，也不执行用户输入的JavaScript。

## 测试与边界

3项TestClient业务回归实际调用ASGI路由，验证非法请求不创建任务、SSE续读不重复progress、会话隔离、取消后不生成final及重复取消409。另有1项页面脚本语法检查：安装Node时检查真实HTML响应中的JavaScript；没有Node则只跳过此可选检查。

TestClient不证明真实socket、浏览器布局、TLS和代理缓冲效果。教学领域层使用内存，重启会丢任务；本课advance接口是明确的人工推进教具，不能当生产队列。

生产延伸到41—43：持久任务与事件，Worker领取租约，审批和幂等。不要让进程内BackgroundTasks承担必须可靠完成的业务写入。

官方依据：[FastAPI请求体](https://fastapi.tiangolo.com/tutorial/body/)、[测试](https://fastapi.tiangolo.com/tutorial/testing/)、[StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/)。
