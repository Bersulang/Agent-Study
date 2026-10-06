"""页面状态与媒体边界教具；实际浏览器和模型见integrations。"""
class PageTask:
    def __init__(self):
        self.state, self.ticket_id = "opened", None

    def submit(self, approved):
        if not approved:
            raise PermissionError("提交操作尚未审批")
        if self.ticket_id is None:
            # 仅教学夹具，不声明创建真实工单。
            self.ticket_id = "DEMO-T-001"
        self.state = "confirmed"
        return self.ticket_id

def check_media(mime, size, maximum=1_000_000):
    allowed = {"image/png", "image/jpeg", "audio/wav", "text/csv", "application/pdf"}
    if mime not in allowed or not 0 < size <= maximum:
        raise ValueError("媒体类型、空文件或大小不合法")
    return {"mime": mime, "size": size}

if __name__ == "__main__":
    page = PageTask()
    try:
        page.submit(False)
    except PermissionError as error:
        print("未审批：", error)
    first = page.submit(True)
    print("页面确认：", first, page.state)
    print("重复提交：", page.submit(True) == first)
    print("媒体校验：", check_media("image/png", 100))
