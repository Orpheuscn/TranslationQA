# 语义对齐 - 翻译质量检查工具

基于深度学习的翻译质量检查工具，支持自动句子对齐、语义相似度计算、翻译异常检测、词对齐等功能。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)

## 🌐 Web版（推荐）

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/Orpheuscn/TranslationQA.git
cd TranslationQA

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装修补过的依赖包（重要！）
pip install patched_packages/dist/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
pip install patched_packages/dist/fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl

# 4. 安装其他依赖
pip install -r requirements.txt

# 5. 下载 LaBSE ONNX 模型（必需，约 1.8GB）
python download_models.py

# 6. 下载 spaCy 模型（可选，用于韩语支持）
python -m spacy download ko_core_news_sm

# 7. 启动服务器
python app.py

# 8. 访问网页
# 打开浏览器访问: http://localhost:5001
```

> **⚠️ 重要**: 
> - 本项目使用了修补过的 `bertalign` 和 `fasttext` 包，必须按照上述步骤安装
> - LaBSE 模型文件约 1.8GB，未包含在 git 仓库中，需要单独下载
> - 详细安装说明请参考 [INSTALL.md](INSTALL.md)

---

## 📚 文档

- **[安装指南](INSTALL.md)** - 详细的安装步骤和常见问题
- **[修补包说明](patched_packages/README.md)** - 为什么需要修补版的依赖包

---

## ✨ 核心功能

- 🔗 **自动句子对齐**: 使用 Bertalign + LaBSE 自动对齐原文和译文，支持 N:M 对齐
- 📊 **语义相似度计算**: 使用 LaBSE 计算句子对的语义相似度，量化翻译质量
- 🔍 **翻译异常检测**: 自动检测缺失 (Omission)、增添 (Addition)、相似度低等问题
- 🔤 **词对齐**: 点击句子对查看词级别的对齐和相似度
- 🌍 **多语言支持**: 支持 100+ 种语言，包括拉丁语、古希腊语等古典语言
- ⚙️ **灵活参数配置**: 9 个可调参数，适应不同翻译场景（直译式、改写式等）
- 🎨 **友好的 Web 界面**: 响应式设计，颜色编码的异常标记，可折叠的高级设置
- 📁 **多格式报告**: JSON 和 CSV 格式，CSV 按源索引排序便于审查
- 🍎 **macOS ARM64 兼容**: 使用 ONNX 版本的 LaBSE，避免 Segmentation fault

## 🚀 Python API使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from translation_qa_tool import TranslationQA

# 初始化工具
qa_tool = TranslationQA(
    similarity_threshold=0.7,    # 相似度阈值
    max_align=6,                 # 最大对齐数
    top_k=5,                     # top-k候选数
    skip=-1.0,                   # 跳过惩罚
    win=10                       # 窗口大小
)

# 检查翻译质量
results = qa_tool.check_translation(
    source_text="Your source text here.",
    target_text="Your target text here.",
    is_split=True  # 如果已分句，设为True
)

# 保存报告
qa_tool.save_report_json(results, "report.json")
qa_tool.save_report_csv(results, "report.csv")

# 打印摘要
qa_tool.print_summary(results)
```

### 运行测试

```bash
python test.py
```

## 📊 输出示例

### CSV报告格式

```csv
原文 (Source),译文 (Target),源索引,目标索引,相似度 (Similarity),异常情况 (Exception)
The Quantum Processor is the core.,量子处理器是核心。,0,0,0.9095,OK
It handles critical computations.,它负责关键计算。,1,1,0.7415,OK
This sentence is omitted.,,2,,,缺失 (Omission)
The system is stable.,系统稳定。,3,2,0.8500,OK
,这是额外的译文。,,3,,增添 (Addition)
```

### JSON报告格式

```json
{
  "metadata": {
    "timestamp": "2024-01-01T12:00:00",
    "source_sentences": 4,
    "target_sentences": 4,
    "alignments_count": 3,
    "similarity_threshold": 0.7
  },
  "alignments": [
    {
      "src_indices": [0],
      "tgt_indices": [0],
      "similarity": 0.9095
    }
  ],
  "issues": {
    "omissions": [...],
    "additions": [...],
    "low_similarity": [...]
  }
}
```

## ⚡ 性能优化建议

### 批量处理多个文档

❌ **错误用法** (每次都重新初始化):

```python
for src, tgt in document_pairs:
    qa_tool = TranslationQA()  # ❌ 重复加载spaCy/HanLP模型
    results = qa_tool.check_translation(src, tgt)
```

✅ **正确用法** (复用实例):

```python
qa_tool = TranslationQA()  # ✅ 只初始化一次
for src, tgt in document_pairs:
    results = qa_tool.check_translation(src, tgt)
```

**性能提升**: 如果启用spaCy，可节省 ~1秒/文档

### 性能说明

- **Bertalign模型**: 全局单例，不会重复加载
- **Embedding计算**: 每次处理新文本都需要（~1.5秒），这是必要开销
- **TextSplitter**: 在`TranslationQA.__init__`中初始化，复用实例可避免重复加载

详见 `性能分析报告.md`

---

## 🔧 参数说明

本工具提供 **9 个可调参数**，分为三类：

### 质量检测参数
- `similarity_threshold` (默认 0.7): 相似度阈值，低于此值标记为"相似度低"
- `force_split_threshold` (默认 0.5): 强制拆散阈值，低于此值拆散为缺失+增添

### Bertalign 对齐参数
- `max_align` (默认 5): N:M 对齐中的 max(N,M)
- `top_k` (默认 3): Bertalign 的 top-k 参数
- `skip` (默认 -1.0): 跳过惩罚，越负越倾向 N:M 对齐
- `win` (默认 5): 窗口大小
- `score_threshold` (默认 0.0): Bertalign 的分数阈值

### 高级功能
- `use_min_similarity` (默认 True): N:M 对齐时使用最小相似度（更严格）
- `auto_split_nm` (默认 True): 自动拆散不合理的 N:N 对齐

**详细说明**: 参见 [参数说明文档](docs/参数说明.md)

---

## 🎯 推荐配置

### 直译式翻译（技术文档、新闻）

```python
qa_tool = TranslationQA(
    similarity_threshold=0.7,
    force_split_threshold=0.5,
    auto_split_nm=True
)
```

### 改写式翻译（戏剧、文学）

```python
qa_tool = TranslationQA(
    similarity_threshold=0.6,
    force_split_threshold=0.4,
    auto_split_nm=False
)
```

**更多配置**: 参见 [参数说明文档](docs/参数说明.md)

## 📁 文件结构

```
.
├── app.py                      # Flask Web 服务器
├── translation_qa_tool.py      # 主工具类
├── labse_onnx_encoder.py       # LaBSE ONNX 编码器
├── text_splitter.py            # 文本分句模块
├── word_aligner.py             # 词对齐模块
├── language_detector.py        # 语言检测模块
├── download_models.py          # 模型下载脚本
├── requirements.txt            # Python 依赖
├── patched_packages/           # 修补过的依赖包
│   ├── dist/                   # 打包好的 wheel 文件
│   └── README.md               # 修补包说明
├── static/                     # Web 前端资源
├── templates/                  # HTML 模板
├── labse_onnx/                 # LaBSE ONNX 模型（需下载）
├── models/                     # FastText 语言检测模型
├── README.md                   # 本文件
└── INSTALL.md                  # 安装指南
```

## 🐛 已修复的问题

### macOS ARM64 兼容性问题

1. **SentenceTransformer 崩溃**: 使用 ONNX Runtime 替代，避免 Segmentation fault
2. **FAISS 批量搜索挂起**: 使用逐个搜索的 workaround
3. **Google Translate API 超时**: 添加可选的语言参数

### NumPy 2.x 兼容性问题

4. **FastText 弃用警告**: 修复 `np.array(copy=False)` 为 `np.asarray()`

### 翻译质量检测问题

5. **空对齐被错误归类**: 修复了 Bertalign 返回空对齐时被归类为"相似度低"的问题
6. **CSV 排序混乱**: 修复了缺失/增添被追加到最后，破坏上下文的问题
7. **N:M 对齐过于保守**: 通过参数调优，支持更复杂的对齐

## 📚 技术栈

- **句子对齐**: Bertalign 1.1.0 (已修补)
- **语义嵌入**: LaBSE ONNX (768维向量)
- **相似度计算**: 余弦相似度（向量平均）
- **分句**: spaCy / HanLP / 简单规则

## ⚠️ 重要说明：Bertalign的对齐行为与强制拆散功能

**Bertalign会尽可能对齐所有句子，很少产生空对齐（缺失/增添）**

### 🆕 强制拆散功能 (Force Split)

为了解决Bertalign的"强制对齐偏差"，我们实现了两个关键功能：

1. **最小相似度策略** (`use_min_similarity=True`): 对N:M对齐，取所有句子对的最小相似度，避免向量平均掩盖不相关句子
2. **强制拆散机制** (`force_split_threshold=0.5`): 将低相似度对齐组拆散为缺失+增添

### 实际异常检测方式

| 异常类型 | 检测方式 | 效果 |
|---------|---------|------|
| 缺失 (Omission) | 强制拆散 (相似度 < 0.5) | ✅ 有效 |
| 增添 (Addition) | 强制拆散 (相似度 < 0.5) | ✅ 有效 |
| 相似度低 | 阈值检测 (0.5 ≤ 相似度 < 0.7) | ✅ 有效 |

### 推荐配置

```python
qa_tool = TranslationQA(
    similarity_threshold=0.7,      # 相似度低阈值
    force_split_threshold=0.5,     # 强制拆散阈值
    use_min_similarity=True        # 使用最小相似度（推荐）
)
```

### 使用建议

查看CSV报告时：
- ✅ 关注"缺失"和"增添"，检查是否合理
- ✅ 关注"相似度低"，检查是否为意译或错译
- ✅ 关注"强制拆散对齐组"数量，评估阈值是否合适

详见 `强制拆散功能说明.md` 和 `Bertalign行为说明.md`

## 🎯 使用场景

- 翻译质量检查
- 双语语料对齐验证
- 翻译遗漏检测
- 翻译增添检测
- 语义歪曲检测

## 📝 许可

MIT License

## 🙏 致谢

- Bertalign: https://github.com/bfsujason/bertalign
- LaBSE: https://huggingface.co/sentence-transformers/LaBSE
- ONNX Runtime: https://onnxruntime.ai/

