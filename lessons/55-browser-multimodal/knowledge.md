# 阶段 55 知识：浏览器与多模态助手项目

[返回讲义](README.md) · [全局知识手册](../../docs/knowledge.md)

### 1. 页面动作与后置条件

使用语义定位寻找控件，动作后检查页面状态或业务结果。元素定位成功只是前置条件；提交后的工单ID、提示或状态才是后置条件。高风险操作仍需要服务端权限。

### 2. 多模态输入与解析

图片、音频、表格和PDF是不同输入形式，需要检查类型、大小、来源和隐私。模型输出仍需校验；OCR可能错字，转写可能漏词，不能把识别结果直接作为授权事实。

### 3. 人工接管与失败恢复

页面变化、登录过期和验证码触发暂停，而非无限重试。保存进度但不记录登录Cookie或敏感截图；恢复前确认页面和业务状态，避免重复提交。

## 执行过程

默认页面状态机模拟打开、提交和确认；未经批准不能提交，重复提交返回原结果；输入检查限制允许的MIME与字节数。真实Playwright脚本操作本地HTML并核验后置条件；Ollama图像与faster-whisper语音适配另见集成目录。

## 新语法

类保存页面状态；None表示尚无结果；MIME是媒体类型标签，但客户端标签本身不可信，真实解析器还需核验内容。

## 判断与排错

| 点击成功但没创建 | 只检查click没有检查结果 | 断言提交后的可见ID或服务端状态 |
| OCR错字变成业务参数 | 未经复核直接执行 | 结构化校验和必要人工确认 |
| 登录失效无限重试 | 失败未分类 | 识别认证故障后暂停并人工接管 |

## 工程边界

默认示例是页面状态教具而非真正浏览器。集成目录含Playwright本地页面、Ollama图像调用、faster-whisper音频转写；模型文件和服务需额外安装，不默认下载或调用。PDF与表格导入关联阶段17。

## 复习问题

区分离线页面状态机与实际浏览器；提交后验证真实结果；解释多模态理解的不确定性和凭证保护。

## 资料

- [Playwright Python](https://playwright.dev/python/docs/intro)。
- [Ollama Chat API](https://docs.ollama.com/api/chat)。
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)。

## Java联系与行为边界

页面测试与Java Selenium的语义定位和结果断言思路接近。PageTask只是状态教具；Playwright实际浏览器单独执行。媒体标签类似HTTP Content-Type，不能单凭声明认为文件安全。

- PageTask初始opened且ticket_id为空；未审批submit立即失败。
- 已批准首次提交形成夹具ID；重复提交复用ID，状态保持confirmed。
- check_media只筛元数据，不证明PNG/PDF解码有效。
- 真实页面脚本在本地HTML fill/click，检查status文本后才判定操作成功。
- 图像脚本调用本地Ollama，音频脚本使用本地模型目录；真实输出必须人工或规则核验。
