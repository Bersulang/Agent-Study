# 实际OpenTelemetry接入

从项目根目录安装和运行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r lessons/46-observability/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/46-observability/integrations/otel_demo.py
```

示例使用真实SDK创建父子Span并验证内存导出，不连接OTLP服务器。生产将导出器替换为OTLP并配置受控endpoint、采样、超时与数据脱敏，不能直接记录完整输入输出。

参考：[官方Python仪表化](https://opentelemetry.io/docs/languages/python/instrumentation/)。
