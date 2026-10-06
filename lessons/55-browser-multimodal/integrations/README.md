# 真实浏览器、图像与语音接入

以下是实际集成代码，不属于默认离线验证。先理解讲义，再按需要安装依赖。

## Playwright本地页面

```powershell
.\.venv\Scripts\python.exe -m pip install -r lessons/55-browser-multimodal/integrations/requirements-browser.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe lessons/55-browser-multimodal/integrations/browser_demo.py
```

脚本启动真正的无界面Chromium并操作本地HTML，不访问外部网站。第一次安装浏览器会下载二进制文件，Linux可能需要额外系统依赖；参阅官方安装文档。

## 图像：本地Ollama

先在Ollama安装并启动你选择的支持图像模型，再运行：

```powershell
$env:OLLAMA_VISION_MODEL = "你已经安装的图像模型名称"
.\.venv\Scripts\python.exe lessons/55-browser-multimodal/integrations/vision_ollama.py path/to/image.png
```

此脚本调用真实本机服务；没有服务或模型时会失败，不伪造识别结果。不上传远程，不将输出用于身份推断或直接执行业务。

## 语音：本地faster-whisper

```powershell
.\.venv\Scripts\python.exe -m pip install -r lessons/55-browser-multimodal/integrations/requirements-audio.txt
$env:WHISPER_MODEL_DIR = "C:\models\whisper-tiny"
.\.venv\Scripts\python.exe lessons/55-browser-multimodal/integrations/audio_whisper.py path/to/sample.wav
```

目录需要预先包含官方支持的转换模型；脚本使用local_files_only避免未经说明的模型下载。默认支持教学限制内的PCM WAV，格式错误不能当作模型识别失败。PDF和表格读取继续参考阶段17。

本机未准备视觉/语音模型，不声称图像与转写效果已验证。浏览器验证结果以根验证报告为准。

资料：[Playwright](https://playwright.dev/python/docs/intro)、[Ollama API](https://docs.ollama.com/api/chat)、[faster-whisper](https://github.com/SYSTRAN/faster-whisper)。
