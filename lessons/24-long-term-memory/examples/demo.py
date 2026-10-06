# 长期记忆的来源与修正：默认标准库、离线、有限退出。
class Memory:
    def __init__(self):
        self.rows = {}

    def put(self, user, key, value, source, expires, consent):
        if not consent:
            raise PermissionError("没有保存授权")
        # 复合键先隔离用户，再识别偏好；不以模型推测的姓名作身份。
        self.rows[(user, key)] = {"value": value, "source": source, "expires": expires}

    def get(self, user, key, now):
        row = self.rows.get((user, key))
        if row is None or now >= row["expires"]:
            return None
        return row["value"]

    def forget(self, user, key):
        self.rows.pop((user, key), None)

def main():
    memory = Memory()
    memory.put("u1", "language", "中文", "用户明确请求", 10, True)
    print(memory.get("u1", "language", 1))
    print(memory.get("u2", "language", 1))
    memory.forget("u1", "language")
    print(memory.get("u1", "language", 1))

if __name__ == "__main__":
    main()
