"""Python标准库HTTP客户端，显式区分HTTP拒绝和网络故障。"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

def fetch_ticket(base_url, user_id='alice', tenant='acme', service_token='local-teaching-token'):
    request = Request(base_url.rstrip('/') + '/api/tickets/T-7', headers={
        'X-Service-Token': service_token, 'X-User-Id': user_id,
        'X-Tenant-Id': tenant, 'X-Trace-Id': 'trace-7'})
    try:
        with urlopen(request, timeout=2) as response:
            body = json.load(response)
            return {'status': response.status, **body}
    except HTTPError as exc:
        # HTTPError仍是可读取的响应对象，须释放连接。
        with exc:
            body = json.load(exc)
            return {'status': exc.code, **body}
    except (URLError, TimeoutError):
        return {'status': 0, 'error': 'network_failure'}

if __name__ == '__main__':
    # 先在另一个终端启动Spring Boot；凭据可通过当前进程环境覆盖。
    token = os.environ.get('TICKET_SERVICE_TOKEN', 'local-teaching-token')
    print(fetch_ticket('http://127.0.0.1:8080', service_token=token))
    print(fetch_ticket('http://127.0.0.1:8080', tenant='other', service_token=token))
