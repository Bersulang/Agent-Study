"""参考答案：先完成练习再阅读；独立执行，不修改学员练习。"""
import json

def solve(data):
    draft = json.loads(data)
    if not isinstance(draft, dict):
        raise ValueError("必须是对象")
    required = {"title", "priority"}
    if not required <= set(draft) or set(draft) - required - {"description"}:
        raise ValueError("字段不符合契约")
    if not isinstance(draft["title"], str) or not draft["title"].strip():
        raise ValueError("title不能为空")
    if type(draft["priority"]) is not int or not 1 <= draft["priority"] <= 5:
        raise ValueError("无效priority")
    if "description" in draft and not isinstance(draft["description"], str):
        raise ValueError("description必须字符串")
    return draft

def limited_chunks(chunks, limit):
    # 限制实际收到的字节数，UTF-8中文不能只按字符数预算。
    used = 0
    for chunk in chunks:
        used += len(chunk)
        if used > limit:
            raise ValueError("流大小超限，未提交草稿")
        yield chunk

if __name__ == "__main__":
    print(solve('{"title":"VPN故障","priority":4,"description":"无法连接"}'))
    try:
        list(limited_chunks([b"123", b"456"], 5))
    except ValueError as error:
        print(f"拒绝：{error}")
