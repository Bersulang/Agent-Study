"""实际OpenTelemetry内存导出，无网络；并不是自定义Trace冒充SDK。"""
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# 每次演示创建独立Provider，避免修改整个进程的全局配置。
exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
tracer = provider.get_tracer("agent-study")
with tracer.start_as_current_span("request"):
    with tracer.start_as_current_span("tool.lookup") as span:
        # 仅记录无敏感值的低基数标签，不记录密钥与业务全文。
        span.set_attribute("tool.name", "lookup")
        span.set_attribute("result.count", 1)
finished = exporter.get_finished_spans()
assert len(finished) == 2
assert finished[0].parent.span_id == finished[1].context.span_id
print("真实SDK父子Span验证：", [span.name for span in finished])
provider.shutdown()
