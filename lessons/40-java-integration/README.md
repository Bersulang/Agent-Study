# 阶段 40：Spring Boot契约与身份

## 使用场景

Python助手调用Java工单业务服务；Java必须自己确认服务身份及租户权限。

主项目仍是企业知识与工单助手。本课用固定工单T-7和政策policy-v2定位边界，避免把模型随机性混进工程机制。

## 学习目标与前置

能构建最小Spring Boot服务，用Python调用，区分401、403、404与超时。

- 前置：阶段39的任务状态与失败处理；阶段03函数、04异常与05字典/集合。
- 本课默认Python 3.12、Windows PowerShell，所有命令从项目根目录执行。
- 演示执行成功与失败分支；运行通过只证明材料可执行，不代表学员已通过验收。

## 关键概念

### 1. 服务身份

定义与用途：证明调用方服务是谁，与用户权限不同。

具体例子：X-Service-Token固定本地示例值只供教学。

### 2. 用户委派

定义与用途：服务请求携带用户身份线索，业务服务仍要核验。

具体例子：Java通过服务端user目录确定alice所属acme，而非相信任意X-Tenant。

### 3. 跨语言契约

定义与用途：双方统一JSON字段、错误对象与状态码，不能依赖Python对象布局。

具体例子：ticket和trace为字符串，状态200/401/403/404明确区分。

### 4. 超时与追踪

定义与用途：请求有限等待并传递关联标识，失败能定位到调用链。

具体例子：Python urlopen(timeout=2)发送X-Trace-Id。

## 演示与默认命令

默认示例只用标准库、离线数据，无API Key；运行有限并退出。

```powershell
python lessons/40-java-integration/examples/demo.py
python -m unittest discover -s lessons/40-java-integration/tests
```

如项目已经建立虚拟环境，将命令中的`python`替换为`.\.venv\Scripts\python.exe`即可；不需要修改执行策略。

`-m unittest`让解释器运行测试模块；`discover -s`指定测试目录。失败时先看断言中的期望与实际差异。

预期业务输出如下（字典键顺序不是业务契约）：

```text
success {'status': 200, 'ticket': 'T-7', 'trace': 'trace-7'}
forbidden {'status': 403, 'error': 'tenant_mismatch'}
unauthenticated {'status': 401, 'error': 'invalid_service_token'}
```

测试应显示`OK`。每个测试固定业务结果，失败案例检查状态、副作用或错误边界。

## 代码与执行过程

下面摘录示例的核心部分，完整文件见[examples/demo.py](examples/demo.py)。

```python
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
```

按执行顺序追踪：

1. 离线authorize_call演示两层验证，先检查服务token。
2. 其次比较租户和scope，拒绝请求没有业务结果。
3. json.dumps/loads保证交换数据采用语言无关结构。
4. integrations Java控制器在服务端固定用户目录核查权限。
5. Python client分别捕获HTTPError和网络错误，不把所有失败都归为模型回答不好。

逐行阅读时先找输入参数，再找校验条件、状态改变、失败返回，最后找资源清理；不要只从print输出反推过程。

### Python语法回顾

- `def`定义函数；参数是调用时传入的值；`return`立刻结束当前函数并交还结果。
- 字典用`对象[键]`读取必需字段，用`.get(键)`读取可选字段；后者缺失时默认返回`None`。
- 集合`set()`用于去重与成员判断；列表保留顺序。字典和列表默认可变，需要明确谁拥有修改权。
- `raise ValueError(...)`表示输入/状态不符合约定；`except ValueError as exc`捕获该类错误，不会自动捕获全部错误。
- `try/finally`保证退出路径清理资源；`with`调用上下文管理协议，具体是否关闭由对象约定决定。
- `if __name__ == "__main__"`只在直接运行文件时执行演示；导入模块进行测试不会自动运行演示。

### 与Java联系和差异

用户已有Java Web经验，本课重点是Python urllib、异常处理和JSON；Java record为不可变传输对象，Python dict默认可变。

## 易错点与排查

- 相信调用方传来的tenant即权限：应从已验证身份解析授权。
- 401和403混用：分别是身份无法验证与身份权限不足。
- Python调用超时后无条件重发写操作：服务可能已提交。

排查顺序：复现固定失败案例 → 查看状态是否改变 → 对照输入契约 → 检查终止条件与清理。不要修改测试期望来掩盖错误。

## 独立练习

在[exercises/practice.py](exercises/practice.py)实现`classify_http_error(status)`。

将401标为authentication、403为authorization、404为not_found、429/503为retryable_read，其他为permanent；只读重试不代表写入安全。

详细样例与要求见[exercises/README.md](exercises/README.md)。骨架的TODO是交给学员的任务，并非缺少课程实现。

```powershell
python lessons/40-java-integration/exercises/practice.py
```

完成练习并解释失败路径后再阅读[solutions/solution.py](solutions/solution.py)。答案是单独的扩展实现，不替代自行练习。

## 能力验收

1. 口头解释“服务身份”与“用户委派”，用本课业务例子说明用途。
2. 不阅读答案，完成练习的正常、边界和失败要求；保留实际运行命令与结果。
3. 手工预测`unauthenticated`案例结果，指出哪些状态改变、哪些状态必须保持。
4. 注释掉一个关键保护条件，解释哪个回归测试应失败；随后恢复代码。
5. 对主项目提出一个新需求，给出输入/输出、权限、预算与失败恢复设计。

通过依据是可运行成果、解释与排错能力；课程材料交付不会自动更新为学员掌握。

## 生产延伸与教学边界

真实环境使用TLS、OAuth2/JWT或mTLS并验证签名、audience、期限及scope；固定token和内存用户目录不是生产认证。

所有模型决策在默认示例中都是确定性替代逻辑；没有测量真实模型质量、价格或联网延迟。集成服务的已执行范围以项目验证报告为准。

## 官方来源与关联知识

可构建Spring Boot工程、Python调用及根目录Maven命令见[integrations/README.md](integrations/README.md)。
本轮只有Python客户端本地HTTP契约测试通过；PATH未发现JDK/Maven，未宣称Java已构建或联调通过。
先在Java环境运行Maven测试和构建，再启动服务运行Python客户端完成真实跨语言验证。

[本课知识说明](knowledge.md)补充状态不变量、错误边界和迁移提示。

- [Python 3.12文档](https://docs.python.org/zh-cn/3.12/)：函数、集合、异常及标准库。
- [Spring Boot系统要求](https://docs.spring.io/spring-boot/3.5/system-requirements.html)：JDK17与Maven要求。
- [Spring REST指南](https://spring.io/guides/gs/rest-service)：控制器与JSON响应。
