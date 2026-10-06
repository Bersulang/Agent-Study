# 真实PDF文件解析与OCR边界

默认演示不安装依赖。本目录专门验证真实PDF文本层；2026-10-06核查pypdf官方文档与PyPI版本。

从项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/17-document-ingestion/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/17-document-ingestion/integrations/pdf_ingest.py --self-test
.\.venv\Scripts\python.exe lessons/17-document-ingestion/integrations/pdf_ingest.py "artifacts/policy.pdf"
python lessons/17-document-ingestion/examples/structured_files.py
```

最后一条只需标准库。真实业务PDF由使用者放入artifacts；课程不假设该文件已存在。
`--self-test`用临时目录产生两页PDF：第1页有文本层，第2页为空。应打印“真实PDF文本提取通过；空白页正确进入质量错误列表”。
使用内部`_add_object`只为测试夹具构造字体与文本流，业务解析使用公开PdfReader API；升级时复验夹具。

## 解析顺序

1. PdfReader读取文件结构；加密文档需要另行授权解密。
2. enumerate从1给每页编号，保留source与page。
3. extract_text读取文本层；空结果进入errors，不丢弃整个文件。
4. 检查页数、空页比例、标题与表格语义，再把合格文字交给分块流程。

PDF保存的是视觉布局；读出的字符顺序不一定等于阅读顺序。多栏、合并单元格、页眉页脚需人工抽样。
CSV例子保留列名与行号；不能把Excel公式或复杂合并表格当作普通CSV自动正确解析。

## OCR安装与责任边界

pypdf不是OCR引擎：扫描图片本身没有可读取字符，需图像识别。先检查是否已有隐藏文本层，避免重复OCR降低质量。
本课不自动安装系统软件。可选方案是Tesseract（需独立安装可执行程序与中文语言数据），或隔离环境里的OCRmyPDF（还涉及Ghostscript等系统依赖）。
Python包装库安装成功不代表OCR二进制和语言包已就绪；在Windows上先用供应商支持的安装方式，或采用WSL/容器，保持业务文件权限边界。
流程为：保存原件 → OCR生成带文本层的新文件 → pypdf提取 → 抽样对照原图 → 标记OCR来源与置信度。
数字、日期、否定词识别错误会改变政策含义，低质量页进入人工检查，不允许直接入库。
本课只验证PDF文本提取和空页检测，没有安装或执行OCR，也没有验证复杂业务PDF准确率。

- [pypdf文本提取官方文档](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [OCRmyPDF安装说明](https://ocrmypdf.readthedocs.io/en/latest/installation.html)
- [Tesseract安装说明](https://tesseract-ocr.github.io/tessdoc/Installation.html)
