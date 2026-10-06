# 最小Spring Boot工单服务与Python调用

`spring-service/`是可构建的真实Maven工程，Spring Boot固定3.5.7，要求JDK17+、Maven3.6.3+。`client.py`使用Python标准库urllib，不需要额外Python依赖。

## 检查环境与构建

以下全部命令从项目根目录执行，不需要切换目录。

```powershell
java -version
mvn -version
mvn -f lessons/40-java-integration/integrations/spring-service/pom.xml test
mvn -f lessons/40-java-integration/integrations/spring-service/pom.xml package
```

`-f`指定pom路径，Maven据此找到标准src/main和src/test目录；首次下载依赖需要网络。`test`运行JUnit/MockMvc；`package`生成target/ticket-service-1.0.0.jar并默认再次执行测试。

## 双终端运行

终端A从项目根目录启动：

```powershell
mvn -f lessons/40-java-integration/integrations/spring-service/pom.xml spring-boot:run
```

终端B仍在项目根目录调用：

```powershell
python lessons/40-java-integration/integrations/client.py
```

预期第一条返回`{'status': 200, 'ticket': 'T-7', 'trace': 'trace-7'}`，第二条返回403及tenant_mismatch。服务只监听127.0.0.1:8080；按Ctrl+C停止。

两端本地默认token都是`local-teaching-token`，它不是秘密也不是生产凭据。想覆盖时，在两个终端分别设置同一`$env:TICKET_SERVICE_TOKEN`；Java由application.properties读取，Python由os.environ读取。不要把真实token写进代码或Git。

## 契约与身份层次

1. Python设置X-Service-Token，证明调用服务身份；缺失或错误返回401。
2. Java固定本地用户目录查alice所属acme及ticket:read权限。X-User-Id只是教学委派线索，生产须验证签名的用户令牌。
3. 请求X-Tenant-Id必须匹配目录中已确定的用户租户；bob属于other，即使头写acme也返回403。
4. T-7固定属于acme；同租户其他工单id返回404。
5. X-Trace-Id贯穿返回以定位请求；这不是权限凭据。

`TicketApplication`触发Spring启动与包扫描；控制器由@RestController和@GetMapping注册接口。Java record定义本地用户目录项，Map.of构造不可变映射。ResponseEntity同时控制状态码和JSON对象，错误体统一error字段。

Python Request构造HTTP请求，`urlopen(timeout=2)`有限等待，`json.load`解析响应。HTTPError代表服务返回4xx/5xx，仍可读错误JSON；URLError/TimeoutError代表网络未能完成请求，返回status0，不伪造服务拒绝。两个分支都释放响应连接。

## 已提供测试与验证边界

```powershell
python -m unittest discover -s lessons/40-java-integration/integrations -p test_client.py
```

Python测试启用本机临时端口探针，实际验证发送身份/追踪头，以及保留401错误JSON；测试结束关闭端口。这个探针不是Spring Boot，不能证明Java构建或Java端点通过。

Java工程含3项JUnit/MockMvc回归：合法alice查询、缺少服务身份401、bob伪造租户403。材料制作环境PATH未发现java或mvn，因此本轮未执行Maven构建、JUnit或Java端到端；需在具备JDK/Maven环境按上述命令验证。

生产认证需TLS、OAuth2/JWT签名与audience/期限核验、服务间mTLS或其他可信凭据。仅拿到合法服务token不足以任意冒充用户。只读失败可按错误分类有限重试；写入必须先处理审批、幂等及状态查证。

官方依据：[Spring REST服务指南](https://spring.io/guides/gs/rest-service)、[Spring Boot3.5系统要求](https://docs.spring.io/spring-boot/3.5/system-requirements.html)、[Python urllib](https://docs.python.org/3.12/library/urllib.request.html)。
