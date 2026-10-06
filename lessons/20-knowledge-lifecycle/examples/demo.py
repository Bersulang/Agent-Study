# 知识生命周期：默认标准库、离线、有限退出。
import hashlib

class Index:
    def __init__(self):
        # 内存字典仅用于教学，进程结束数据消失。
        self.documents = {}
        self.generation = 0

    def update(self, identity, text, expires=None):
        if not text.strip():
            raise ValueError("空内容不能覆盖有效版本")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        old = self.documents.get(identity)
        # 正文相同但生效元数据变化也必须更新版本，不能只比较内容摘要。
        if old and old["digest"] == digest and old["expires"] == expires:
            return "unchanged"
        version = old["version"] + 1 if old else 1
        self.documents[identity] = {"text": text, "digest": digest, "version": version, "expires": expires}
        self.generation += 1
        return "updated"

    def delete(self, identity):
        if identity in self.documents:
            del self.documents[identity]
            self.generation += 1

    def visible(self, now):
        # 过期对象仍可用于审计，但不能进入读服务；返回副本避免污染索引。
        return {identity: dict(row) for identity, row in self.documents.items()
                if row["expires"] is None or now < row["expires"]}

def main():
    index = Index()
    print(index.update("policy", "限额500"))
    print(index.update("policy", "限额800"))
    print(index.documents["policy"]["version"])
    index.delete("policy")
    print(index.documents)

if __name__ == "__main__":
    main()
