"""跨服务契约离线验证；不是 Spring Boot，真实工程在 integrations。"""
import json

def authorize_call(claims, ticket, service_token):
    # 本地固定凭据仅用于说明身份层次，不是生产认证实现。
    if service_token != "local-teaching-token":
        return {"status": 401, "error": "invalid_service_token"}
    if claims.get("tenant") != ticket["tenant"]:
        return {"status": 403, "error": "tenant_mismatch"}
    if "ticket:read" not in claims.get("scopes", []):
        return {"status": 403, "error": "scope_missing"}
    return {"status": 200, "ticket": ticket["id"], "trace": claims["trace"]}

def run_case(case):
    # JSON 往返验证 Python/Java 都能理解的字符串、数组契约。
    claims = json.loads(json.dumps({"tenant": "acme", "scopes": ["ticket:read"], "trace": "trace-7"}))
    if case == "forbidden":
        claims["tenant"] = "other"
    token = "wrong" if case == "unauthenticated" else "local-teaching-token"
    return authorize_call(claims, {"id": "T-7", "tenant": "acme"}, token)

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['success', 'forbidden', 'unauthenticated']:
        print(case, run_case(case))
