"""内存幂等教学夹具；模拟写入后响应丢失，不访问网络。"""
class Store:
    def __init__(self):
        self.tickets = []
        self.requests = {}

    def create(self, key, title):
        if key in self.requests:
            old_title, result = self.requests[key]
            if old_title != title:
                raise ValueError("同一幂等键不能绑定不同参数")
            return result.copy()
        result = {"id": f"T{len(self.tickets) + 1}", "title": title}
        # 教学中同步写入两份内存记录；生产必须放同一数据库事务。
        self.tickets.append(result)
        self.requests[key] = (title, result)
        raise TimeoutError("写入成功但响应丢失")

def retry_create(store, key, title, attempts=2, allowed=True):
    if not allowed:
        raise PermissionError("未授权，不执行写入")
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError("attempts必须为1到3整数")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("幂等键不能为空")
    if not isinstance(title, str) or not title.strip() or len(title) > 100:
        raise ValueError("标题长度必须为1到100字符")
    for attempt in range(attempts):
        try:
            return store.create(key, title)
        except TimeoutError:
            # 只重试超时，沿用原键与参数；最后一次仍失败就传播。
            if attempt == attempts - 1:
                raise

if __name__ == "__main__":
    store = Store()
    print(f"最终结果：{retry_create(store, 'request-1', '登录失败')}")
    print(f"实际写入数：{len(store.tickets)}")
    try:
        retry_create(store, "request-1", "改过的标题")
    except ValueError as error:
        print(f"拒绝：{error}")
