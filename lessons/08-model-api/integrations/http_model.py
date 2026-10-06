"""真实Chat Completions HTTP适配；显式运行才发送请求。

只支持符合该请求/响应形状的端点，不声称兼容所有模型供应商。
不自动重试付费调用，不在错误中记录密钥或完整供应商正文。
"""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPErrorProcessor, Request, build_opener


class ModelAPIError(RuntimeError):
    """接口层失败；与回答事实错误分别处理。"""


class RejectRedirects(HTTPErrorProcessor):
    """在默认重定向处理器创建下一请求之前，统一拒绝全部3xx。"""

    def http_response(self, request, response):
        if 300 <= response.code < 400:
            # 不读取Location、不创建跳转请求，也不把敏感响应正文放进异常。
            status = response.code
            response.close()
            raise ModelAPIError(f"HTTP {status}；已拒绝重定向，请核查配置的最终HTTPS端点")
        return super().http_response(request, response)

    # 同一门禁同时处理HTTP和HTTPS响应，包含307/308。
    https_response = http_response


def open_request(request, timeout):
    # 私有opener替换默认HTTPErrorProcessor；不修改应用全局urllib配置。
    return build_opener(RejectRedirects()).open(request, timeout=timeout)


class HTTPModel:
    def __init__(self, base_url, api_key, model, timeout=30):
        if not api_key or not model:
            raise ValueError("必须配置环境变量密钥与模型名称")
        parsed = urlparse(base_url)
        # 真实密钥只能经HTTPS发送；本课Mock不需要放宽该边界。
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("模型地址必须是无内嵌凭证的HTTPS URL")
        if parsed.query or parsed.fragment or timeout <= 0:
            raise ValueError("地址不能带查询/片段，timeout必须为正")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, messages):
        # 基础文本请求；不假定temperature/max_tokens等选项被所有模型支持。
        payload = {"model": self.model, "messages": messages, "stream": False}
        request = Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.api_key},
            method="POST",
        )
        try:
            with open_request(request, timeout=self.timeout) as response:
                # 防止错误端点返回超大正文；生产可配置更合适上限。
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise ModelAPIError("模型响应大小超限")
                result = json.loads(raw.decode("utf-8"))
        except HTTPError as error:
            raise ModelAPIError(f"HTTP {error.code}；检查凭证、额度或服务状态") from None
        except (URLError, TimeoutError) as error:
            raise ModelAPIError(f"网络调用失败：{type(error).__name__}") from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ModelAPIError("响应不是有效UTF-8 JSON") from None
        try:
            message = result["choices"][0]["message"]
            if message.get("refusal"):
                raise ModelAPIError("模型拒答；未生成业务结果")
            text = message["content"]
            if not isinstance(text, str):
                raise ModelAPIError("响应非文本；需接入专用内容块或工具调用适配")
            usage = result.get("usage") or {}
            return {"text": text, "usage": {
                "input_tokens": usage.get("prompt_tokens"),
                "output_tokens": usage.get("completion_tokens"),
            }}
        except (KeyError, IndexError, TypeError, AttributeError):
            raise ModelAPIError("响应不符合当前Chat Completions适配契约") from None


def main():
    # 未配置时在发请求前失败；不索取、不打印密钥。
    adapter = HTTPModel(
        os.environ.get("MODEL_BASE_URL", "https://api.openai.com/v1"),
        os.environ.get("MODEL_API_KEY", ""),
        os.environ.get("MODEL_NAME", ""),
    )
    response = adapter.complete([
        {"role": "user", "content": "这是接口连通性测试，请只回答OK。"}
    ])
    print(response["text"])
    print(f"供应商报告用量：{response['usage']}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, ModelAPIError) as error:
        raise SystemExit(str(error))
