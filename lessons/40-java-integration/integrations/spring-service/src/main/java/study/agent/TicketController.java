package study.agent;

import java.util.Map;
import java.util.Set;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

/** 服务端自己核验服务身份和用户目录，不能相信调用方任意声称的租户。 */
@RestController
public class TicketController {
    // 本地固定目录替代认证服务：生产须验证JWT/mTLS并查询真实授权。
    private record User(String tenant, Set<String> scopes) {}
    private final Map<String, User> users = Map.of("alice", new User("acme", Set.of("ticket:read")),
                                                  "bob", new User("other", Set.of("ticket:read")));
    private final String serviceToken;

    public TicketController(@Value("${ticket.service-token:local-teaching-token}") String serviceToken) {
        this.serviceToken = serviceToken;
    }

    @GetMapping("/api/tickets/{id}")
    public ResponseEntity<Map<String, String>> read(
            @PathVariable String id,
            @RequestHeader(value="X-Service-Token", defaultValue="") String token,
            @RequestHeader(value="X-User-Id", defaultValue="") String userId,
            @RequestHeader(value="X-Tenant-Id", defaultValue="") String requestedTenant,
            @RequestHeader(value="X-Trace-Id", defaultValue="") String trace) {
        // 401：尚未验证服务身份；不能先返回用户目录信息。
        if (serviceToken.isBlank() || !serviceToken.equals(token)) {
            return error(401, "invalid_service_token");
        }
        User user = users.get(userId);
        // 403：服务已验证，但委派用户不存在或租户声明不匹配。
        if (user == null || !user.tenant().equals(requestedTenant) || !user.scopes().contains("ticket:read")) {
            return error(403, "tenant_mismatch");
        }
        // 固定教学工单属于acme，其他租户即使有读取scope也不能读取。
        if (!user.tenant().equals("acme")) {
            return error(403, "tenant_mismatch");
        }
        if (!id.equals("T-7")) {
            return error(404, "ticket_not_found");
        }
        return ResponseEntity.ok(Map.of("ticket", id, "trace", trace));
    }

    private ResponseEntity<Map<String, String>> error(int status, String code) {
        // 响应契约固定为JSON对象，不把堆栈和凭据输出给客户端。
        return ResponseEntity.status(status).body(Map.of("error", code));
    }
}
