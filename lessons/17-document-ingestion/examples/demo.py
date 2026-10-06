# 文档导入与质量检查：默认标准库、离线、有限退出。
import hashlib

def ingest(text, source, size=24):
    # 空白不是可用知识；在导入阶段拒绝，避免检索伪造出处。
    if not text.strip():
        raise ValueError("没有可提取文字，需要检查文本层或OCR")
    if size <= 0:
        raise ValueError("分块长度必须为正数")
    chunks = []
    # enumerate 从1开始保留自然段位置；空行是本例的段落边界。
    for paragraph, body in enumerate(text.split("\n\n"), 1):
        body = body.strip()
        for start in range(0, len(body), size):
            piece = body[start:start + size]
            digest = hashlib.sha256(piece.encode("utf-8")).hexdigest()[:12]
            chunks.append({"source": source, "paragraph": paragraph,
                           "offset": start, "id": digest, "text": piece})
    return chunks

def main():
    for chunk in ingest("# 报销规则\n出差交通费需要发票。\n\n审批后才能付款。", "policy.md"):
        print(chunk["source"], chunk["paragraph"], chunk["offset"], chunk["text"])

if __name__ == "__main__":
    main()
