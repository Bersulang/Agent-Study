"""可选真实语义向量：模型下载不是默认课程运行的一部分。"""
from sentence_transformers import SentenceTransformer


def main():
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    texts = ["Travel reimbursement requires a receipt.", "Reset your password through support."]
    # encode输出的是训练模型生成的真实embedding，不是哈希或词项计分。
    vectors = model.encode(texts + ["How do I prove my travel expenses?"], normalize_embeddings=True)
    similarities = model.similarity(vectors[-1:], vectors[:-1])[0]
    for score, text in sorted(zip(similarities.tolist(), texts), reverse=True):
        print(round(score, 4), text)


if __name__ == "__main__":
    main()
