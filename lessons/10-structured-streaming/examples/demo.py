"""真实SSE文本边界解析；本地字节流是教学夹具。"""
import codecs
import json

class StreamCancelled(Exception):
    """调用者取消，不允许提交半成品。"""

def sse_events(chunks):
    decoder = codecs.getincrementaldecoder("utf-8")()
    buffer = ""
    data = []
    first = True
    for chunk in chunks:
        text = decoder.decode(chunk)
        if first and text:
            text = text.removeprefix("\ufeff")
            first = False
        buffer += text
        # 同时识别LF、CRLF、CR；末尾CR需等下一块确认是否CRLF。
        while True:
            positions = [i for i, char in enumerate(buffer) if char in "\r\n"]
            if not positions:
                break
            end = positions[0]
            if buffer[end] == "\r" and end == len(buffer) - 1:
                break
            width = 2 if buffer[end:end + 2] == "\r\n" else 1
            line, buffer = buffer[:end], buffer[end + width:]
            if line == "":
                if data:
                    yield "\n".join(data)
                    data = []
            elif not line.startswith(":"):
                field, separator, value = line.partition(":")
                if value.startswith(" "):
                    value = value[1:]
                if field == "data":
                    data.append(value if separator else "")
    # 检查残缺UTF-8；EOF不把未结束事件提交。
    decoder.decode(b"", final=True)
    if buffer == "\r" and data:
        # 一个尾部CR结束空行，此时确实有事件边界。
        yield "\n".join(data)

def validate_draft(value):
    if not isinstance(value, dict) or set(value) != {"title", "priority"}:
        raise ValueError("字段必须恰好为title和priority")
    if not isinstance(value["title"], str) or not value["title"].strip():
        raise ValueError("title必须非空")
    if type(value["priority"]) is not int or not 1 <= value["priority"] <= 5:
        raise ValueError("priority必须为1到5整数")
    return value

def collect_draft(chunks, cancelled=lambda: False):
    parts = []
    done = False
    for event in sse_events(chunks):
        if cancelled():
            raise StreamCancelled("已取消，草稿未提交")
        if event == "[DONE]":
            done = True
            break
        parts.append(event)
    if cancelled():
        raise StreamCancelled("已取消，草稿未提交")
    if not done:
        raise ValueError("流未完整结束，草稿未提交")
    return validate_draft(json.loads("".join(parts)))

if __name__ == "__main__":
    # 模拟应用直接在data中发文本；真实供应商常发JSON envelope，需要适配。
    wire = 'data: {"title":"登录失败",\n\ndata: "priority":4}\n\ndata: [DONE]\n\n'.encode()
    chunks = [wire[i:i + 3] for i in range(0, len(wire), 3)]
    print(f"已校验草稿：{collect_draft(chunks)}")
    try:
        collect_draft([b'data: {"title":\n\n'])
    except ValueError as error:
        print(f"拒绝：{error}")
