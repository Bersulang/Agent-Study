# 真实Embedding接入

默认examples是词项检索，不是embedding。本目录提供两个真实向量提供器选择；2026-10-06核查官方文档。
不要求学员提前安装模型或索取密钥；选定路线后再准备外部环境。

## 路线A：Ollama本地HTTP提供器

Python适配器只用标准库。需另行安装Ollama、启动本地服务并下载支持embedding的模型。
Ollama应用版本由安装渠道确定，记录 `ollama --version`；模型标签可变，记录/api/tags返回的digest才可复现实验。
此适配按官方/api/embed接口编写，固定路径、字段和30秒超时；兼容性应通过实际服务响应验证。

从项目根目录执行（Ollama已安装后）：

```powershell
ollama --version
ollama pull embeddinggemma
ollama list
python lessons/18-basic-rag/integrations/ollama_embeddings.py --model embeddinggemma
```

`pull`会下载模型，需网络和磁盘空间；模型名称是示例而不是企业适配建议。
适配器把文档和问题一起发送给同一模型，检查数量、维度、有限数值，再计算余弦排序。
固定词检索和语义检索结果可能不同，记录前两条来源和分数，不能把“最高分”当成已证明问题有答案。
truncate=False让超长输入明确报错，而非静默截断政策。生产批处理应限制文本大小与批次并记录模型版本。

## 路线B：SentenceTransformer

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r lessons/18-basic-rag/integrations/requirements.txt
.\.venv\Scripts\python.exe lessons/18-basic-rag/integrations/sentence_transformer_demo.py
```

sentence-transformers固定6.1.0；依赖PyTorch，安装体积较大；第一次运行还需下载模型权重。
all-MiniLM-L6-v2主要为英文场景，本例使用英文只为观察同义改写；中文企业数据需独立评估合适的模型。
encode生成真实学习到的数值向量，normalize_embeddings归一化；similarity比较查询与文档。
生产应固定模型仓库revision和向量维度，把模型、分块、索引版本一起记录，升级后重建并评估。

## 本次验证范围

已验证适配器语法、余弦计算和本地HTTP契约测试；契约夹具不是实际模型。
没有安装Ollama、下载模型或运行SentenceTransformer权重，所以不声称实际embedding质量或端到端模型接入通过。
外部服务不可用时应明确失败，不切换到伪造embedding冒充成功。

- [Ollama embed接口](https://docs.ollama.com/api/embed)
- [Ollama模型清单与digest](https://docs.ollama.com/api/tags)
- [SentenceTransformer语义检索](https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)
