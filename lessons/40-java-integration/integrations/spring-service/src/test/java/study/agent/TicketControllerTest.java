package study.agent;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/** 检查业务授权结果；需JDK17/Maven运行，Python HTTP探针不能替代本测试。 */
@SpringBootTest
@AutoConfigureMockMvc
class TicketControllerTest {
    @Autowired private MockMvc mvc;

    @Test void acceptedUserGetsTicketAndTrace() throws Exception {
        mvc.perform(get("/api/tickets/T-7").header("X-Service-Token", "local-teaching-token")
            .header("X-User-Id", "alice").header("X-Tenant-Id", "acme").header("X-Trace-Id", "trace-7"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.ticket").value("T-7"))
            .andExpect(jsonPath("$.trace").value("trace-7"));
    }
    @Test void missingServiceIdentityIsUnauthorized() throws Exception {
        mvc.perform(get("/api/tickets/T-7")).andExpect(status().isUnauthorized());
    }
    @Test void userCannotInventAnotherTenant() throws Exception {
        mvc.perform(get("/api/tickets/T-7").header("X-Service-Token", "local-teaching-token")
            .header("X-User-Id", "bob").header("X-Tenant-Id", "acme"))
            .andExpect(status().isForbidden()).andExpect(jsonPath("$.error").value("tenant_mismatch"));
    }
}
