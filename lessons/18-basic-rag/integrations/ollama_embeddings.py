"""真实Ollama /api/embed适配：标准库HTTP，需另行运行本地Ollama和下载模型。"""
import argparse
import json
import math
from urllib.request import Request, urlopen


class OllamaEmbeddings:
    def __init__(self, model, base_url="http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def embed(self, texts):
        # 参数必须使用同一模型生成库向量与查询向量，不能混合不同维度空间。
        payload = json.dumps({"model": self.model, "input": texts, "truncate": False}).encode("utf-8")
        request = Request(self.base_url + "/api/embed", data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        vectors = result.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise ValueError("embedding数量与输入不一致")
        if not vectors or not vectors[0]:
            raise ValueError("服务没有返回有效向量")
        size = len(vectors[0])
        for vector in vectors:
            if len(vector) != size or any(not isinstance(x, (float, int)) or not math.isfinite(x) for x in vector):
                raise ValueError("向量维度或数值异常")
        return vectors


def cosine(left, right):
    if len(left) != len(right):
        raise ValueError("向量维度不同，不能比较")
    length = math.sqrt(sum(x*x for x in left) * sum(x*x for x in right))
    if length == 0:
        raise ValueError("零向量没有可用余弦相似度")
    return sum(a*b for a, b in zip(left, right)) / length


def main():
    parser = argparse.ArgumentParser(description="真实本地embedding检索，不调用生成模型")
    parser.add_argument("--model", default="embeddinggemma")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    args = parser.parse_args()
    provider = OllamaEmbeddings(args.model, args.base_url)
    docs = [{"text": "Reimbursement requires a receipt.", "source": "policy.md#1"},
            {"text": "Reset passwords using the support portal.", "source": "security.md#1"}]
    question = "What proof do I need for travel expenses?"
    vectors = provider.embed([doc["text"] for doc in docs] + [question])
    ranked = sorted([(cosine(vector, vectors[-1]), doc) for vector, doc in zip(vectors[:-1], docs)], key=lambda row: -row[0])
    for score, doc in ranked:
        print(round(score, 4), doc["source"], doc["text"])
    # 最相似不等于证据充分；阈值需用自己的问题集标注与校准。


if __name__ == "__main__":
    main()
