# 上下文工程：默认标准库、离线、有限退出。
def pack(items, budget):
    if budget < 0:
        raise ValueError("预算必须非负")
    selected, dropped, used = [], [], 0
    ordered = sorted(items, key=lambda item: -item["priority"])
    for item in ordered:
        # 字符计数只是容量教学代理，不等于供应商tokenizer。
        cost = len(item["text"])
        if used + cost <= budget:
            selected.append(dict(item))
            used += cost
        elif item.get("required", False):
            raise ValueError("必要上下文放不下，不能静默裁剪约束")
        else:
            dropped.append(item["id"])
    return {"selected": selected, "dropped": dropped, "used": used}

def main():
    items = [{"id": "rule", "text": "必须审批", "priority": 100, "required": True},
             {"id": "evidence", "text": "发票有效", "priority": 50},
             {"id": "history", "text": "昨天闲聊内容较长", "priority": 1}]
    print(pack(items, 8))

if __name__ == "__main__":
    main()
