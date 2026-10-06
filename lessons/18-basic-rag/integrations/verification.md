# Embedding适配验证范围

2026-10-06，Python 3.12.10；项目根目录执行：

```powershell
python -m unittest discover -s lessons/18-basic-rag/tests -v
```

实际退出码0，3个测试通过：无证据与引用边界、余弦维度与零向量边界、本机HTTP请求响应映射。
HTTP测试启动回环夹具，验证/api/embed路径、model/input字段、truncate=False及向量数量；结束后关闭服务器与线程。
夹具向量是固定测试数值，不是模型产生的embedding，不据此评价语义质量。

所有本目录Python文件均通过ast.parse语法检查；Ollama适配只需标准库。
未安装Ollama或SentenceTransformer，没有模型权重下载、真实embedding生成、语义质量评估或向量库规模测试。
真实执行方法与依赖在README.md与requirements.txt；外部模型未验证的状态不能写成通过。
