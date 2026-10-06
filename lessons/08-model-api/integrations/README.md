# 真实模型HTTP接入

默认 `examples/demo.py` 完全离线。本目录会发出真实模型请求，可能计费。
本次材料制作没有调用付费模型；Mock测试验证请求形状、错误路径和响应转换，不证明真实账号连通。

## 供应商兼容边界

2026-10-06核查 [OpenAI Chat API官方资料](https://developers.openai.com/api/reference/resources/chat)。
本适配器只实现文本Chat Completions的 `POST /chat/completions`，请求包含model/messages/stream。
它使用标准库urllib，未安装或伪装官方SDK。
OpenAI的Responses API、其他供应商原生Messages API、工具调用内容块等不能直接交给本实现。
“兼容端点”需明确支持相同请求、认证方式与响应字段，不能只看供应商宣传名称。
模型列表、角色、上下文窗口、计费、参数能力需接入时从目标供应商官方文档再确认。
本示例不默认指定某个模型，也不把教学费率当真实价格。

## PowerShell配置与运行

命令工作目录为项目根目录；Python 3.12标准库即可。
自行用已有密钥管理方案设置环境变量，不把密钥字面值写入脚本或提交仓库。
以下使用PowerShell掩码输入，避免密钥出现在命令历史中。

```powershell
# 根据你已确认的供应商端点配置；默认值仅用于OpenAI Chat接口。
$env:MODEL_BASE_URL = 'https://api.openai.com/v1'
$env:MODEL_NAME = Read-Host '输入账号已支持的模型ID'
$modelSecret = Read-Host '输入你已有的API密钥' -AsSecureString
$modelCredential = [System.Net.NetworkCredential]::new('', $modelSecret)
$env:MODEL_API_KEY = $modelCredential.Password
python lessons/08-model-api/integrations/http_model.py
Remove-Item Env:MODEL_API_KEY
Remove-Variable modelCredential, modelSecret
```

`$env:NAME`设置当前进程与子进程环境；`Read-Host`读取终端输入。
`-AsSecureString`掩码显示输入，转成进程环境后仍属于明文进程数据，需遵循企业密钥规范。
此处只用测试问题，无真实工单和客户资料。
未设置MODEL_API_KEY或MODEL_NAME时直接退出，不发请求。

## 离线契约验证

```powershell
python -m unittest discover -s lessons/08-model-api/tests -v
```

基础契约测试用fake密钥与example.test地址，open_request被Mock替换，不访问网络。
重定向测试保留真实urllib处理链，只替换HTTPHandler/HTTPSHandler的最终传输，不建立网络连接。
覆盖JSON请求、用量转换、401脱敏、拒答、缺密钥、非HTTPS端点、跨源与降级跳转拒绝。
共8个测试方法，其中一个使用subTest枚举300—399全部状态码，包含307/308。
30秒是urllib socket timeout，不是覆盖所有重试和连接阶段的业务总期限。
教学适配未实现流式、代理策略、TLS定制、退避与分布式预算；按后续阶段补充。

## 排错

- 401：核查密钥是否有效、认证方式是否属于该供应商；不要打印密钥。
- 404：核查base URL、API路径和model；不能把原生API当兼容API。
- 429：区分限流与额度不足；本示例不盲目重试付费请求。
- 200但无文本：可能返回拒答、工具调用或非文本块，需专用适配。
- 无usage：结果字段为None，表示未知，不能按零费用计账。
- 答案有误：这不是HTTP故障，应做证据核查和任务评估。
- 3xx：本适配拒绝所有跳转，核查并配置供应商最终HTTPS地址，不自动重发认证信息。

## HTTPS初始地址不能代替重定向边界

初始请求为HTTPS只说明第一次传输受TLS保护，不代表服务器不会返回Location跳到别处。
本项目Python 3.12.10默认HTTPRedirectHandler对POST的301/302/303可自动构造新请求。
核查其源码发现：它过滤Content-Length/Content-Type，但保留Authorization，且允许HTTP目标。
因此跨源HTTPS跳转可能把密钥交给其他服务器，HTTPS→HTTP跳转还可能把认证信息放到明文传输。
默认POST对307/308不采用相同自动跳转行为，但客户端不能把这一差异当成明确的安全策略。

本适配采用“所有300—399响应均拒绝”的清楚规则。
`RejectRedirects`继承HTTPErrorProcessor，在默认重定向处理链创建下一请求之前关闭响应并抛接口错误。
`https_response = http_response`让同一门禁覆盖HTTPS；HTTP路径也有相同限制。
`build_opener`创建本次调用的私有处理链，不使用install_opener修改全局设置。
错误仅包含状态码和配置建议，不包含Token、Location地址或响应正文。

2026-10-06实际先运行新增离线回归，原实现跨源/降级案例未抛拒绝错误，测试失败。
改为私有拒绝策略后8个测试方法通过，每种3xx只有第一次模拟传输，没有第二次请求。
所有核查均使用fake-token和example.test地址，未使用真实密钥、未发送付费请求。
[urllib.request官方处理链说明](https://docs.python.org/3.12/library/urllib.request.html)。
