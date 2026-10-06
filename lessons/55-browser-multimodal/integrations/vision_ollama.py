"""真实Ollama图像接口；仅手动执行，要求已运行本地多模态模型。"""
import argparse
import base64
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument("image", type=Path, help="你有权处理的PNG/JPEG文件")
args = parser.parse_args()
model = os.environ.get("OLLAMA_VISION_MODEL")
if not model:
    raise SystemExit("先设置OLLAMA_VISION_MODEL，使用已安装且支持图像的模型")
data = args.image.read_bytes()
if not 0 < len(data) <= 1_000_000:
    raise SystemExit("图片为空或超过1MB教学限制")
if not (data.startswith(b"\x89PNG\r\n\x1a\n") or data.startswith(b"\xff\xd8\xff")):
    raise SystemExit("需要PNG/JPEG；头部检查仍不能替代完整安全解码")
body = {"model": model, "stream": False, "messages": [
    {"role": "user", "content": "描述图片中可观察到的内容，不猜测身份。",
     "images": [base64.b64encode(data).decode("ascii")]}]}
request = Request("http://127.0.0.1:11434/api/chat", data=json.dumps(body).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
with urlopen(request, timeout=60) as response:
    result = json.loads(response.read(2_000_000))
# 这是未经事实验证的模型识别文本，不得直接触发业务工具。
print(result["message"]["content"])
