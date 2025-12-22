# 翻译质量检查工具

自动化翻译质量检查工具，用于检测翻译中的三种异常：缺失、增添、语义歪曲。

## 功能特性

- ✅ **N:M句子对齐**: 使用Bertalign进行多对多语义对齐
- ✅ **跨语言相似度**: 使用LaBSE ONNX模型计算语义相似度
- ✅ **三种异常检测**:
  - 缺失 (Omission): 原文句子在译文中没有对应
  - 增添 (Addition): 译文句子在原文中没有对应
  - 相似度低 (Low Similarity): 对齐组相似度低于阈值
- ✅ **自动分句**: 支持spaCy（英文）和HanLP（中文）
- ✅ **多格式报告**: JSON和CSV格式输出

## 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 核心依赖已安装：
# - bertalign
# - onnxruntime
# - transformers
# - pandas
# - numpy

# 可选：安装分句工具（如需要）
pip install spacy
python -m spacy download en_core_web_sm

pip install hanlp
```

## 快速开始

```python
from translation_qa_tool import TranslationQA

# 初始化工具（使用优化后的默认参数）
qa_tool = TranslationQA(
    similarity_threshold=0.7,    # 相似度阈值
    max_align=6,                 # 最大对齐数（支持复杂N:M对齐）
    top_k=5,                     # top-k候选数
    score_threshold=0.15,        # Bertalign分数阈值
    skip=-1.0,                   # 跳过惩罚（强惩罚，倾向N:M对齐）
    win=10                       # 窗口大小
)

# 检查翻译（自动分句）
results = qa_tool.check_translation(
    source_text="Your source text here.",
    target_text="你的译文在这里。",
    is_split=False  # 自动分句
)

# 查看结果
qa_tool.print_summary(results)

# 保存报告
qa_tool.save_report_json(results, "report.json")
qa_tool.save_report_csv(results, "report.csv")
```

## 文件结构

```
语义对齐/
├── labse_onnx/                  # LaBSE ONNX模型
├── translation_qa_tool.py       # 主工具
├── labse_onnx_encoder.py        # ONNX编码器
├── text_splitter.py             # 分句模块
├── test.py                      # 测试脚本
└── README_FINAL.md              # 本文档
```

## 技术栈

- **句子对齐**: Bertalign (max_align=6, skip=-1.0, top_k=5, win=10)
- **语义嵌入**: LaBSE ONNX (768维向量)
- **相似度计算**: 余弦相似度（向量平均）
- **分句**: spaCy / HanLP / 简单规则

## 参数说明

### Bertalign参数优化

经过测试，以下参数组合能够实现最佳的N:M对齐效果：

- `max_align=6`: 支持最多6:6的对齐（如4:2, 3:3等复杂对齐）
- `skip=-1.0`: 强惩罚"跳过"（缺失/增添），使算法更倾向于N:M对齐
- `top_k=5`: 增加候选数，提高对齐质量
- `win=10`: 扩大搜索窗口，捕捉更远距离的对齐

这些参数的调整解决了原始Bertalign过于保守的问题，能够正确识别复杂的句子重组情况。

## CSV报告格式

CSV报告按照以下格式展开1:N和N:1对齐：

| 原文 (Source) | 译文 (Target) | 源索引 | 目标索引 | 相似度 | 异常情况 |
|--------------|--------------|--------|---------|--------|---------|
| Sentence 1   | 句子1        | 0      | 0       | 0.95   | OK      |
| Sentence 2   | 句子2        | 1      | 1       | 0.85   | OK      |
| Sentence 3   | 句子3        | 2      | 2       | 0.65   | 相似度低 |

## 测试

```bash
source venv/bin/activate
python test.py
```

## 许可证

MIT License

