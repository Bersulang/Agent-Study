# 远程MCP与故障边界：默认标准库、离线、有限退出。
class RemoteError(Exception):
    pass

def call_read(operation, attempts=2):
    if attempts < 1:
        raise ValueError("尝试次数至少为1")
    for attempt in range(attempts):
        try:
            return operation()
        except ConnectionError:
            # 仅针对只读调用的断连重试；权限错误会直接向外传播。
            if attempt == attempts - 1:
                raise RemoteError("重连预算耗尽")

def compatible(required, discovered):
    missing = set(required) - set(discovered)
    if missing:
        raise RemoteError("服务缺少工具：" + ",".join(sorted(missing)))
    return True

def main():
    calls = []
    def service():
        calls.append(1)
        if len(calls) == 1:
            raise ConnectionError("模拟断连")
        return {"ticket": "T1", "status": "open"}
    print(call_read(service))
    print("attempts", len(calls))
    print(compatible(["get_ticket"], ["get_ticket"]))

if __name__ == "__main__":
    main()
