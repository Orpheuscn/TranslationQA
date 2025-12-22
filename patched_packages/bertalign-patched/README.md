# Bertalign (macOS ARM64 Patched Version)

这是Bertalign的修补版本，专门针对macOS ARM64平台的兼容性问题进行了修复。

## 修复内容

### 1. encoder.py - 使用ONNX替代SentenceTransformer
- **问题**: SentenceTransformer在macOS ARM64上会导致Segmentation Fault崩溃
- **修复**: 使用ONNX Runtime加载LaBSE模型，避免PyTorch相关的崩溃问题
- **影响**: 完全重写 (+52行, -24行)

### 2. aligner.py - 添加语言参数
- **问题**: 每次都调用Google Translate API检测语言，容易超时
- **修复**: 添加`src_lang`和`tgt_lang`可选参数，允许手动指定语言
- **影响**: 添加参数 (+8行, -2行)

### 3. corelib.py - 修复FAISS批量搜索
- **问题**: FAISS在macOS ARM64上批量搜索会挂起
- **修复**: 使用逐个搜索替代批量搜索
- **影响**: 修复bug (+18行, -3行)

## 安装

```bash
pip install bertalign-macos-patched-0.1.0.post1.tar.gz
# 或
pip install bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
```

## 使用

使用方法与原版Bertalign完全相同，但需要：

1. **准备ONNX模型**: 需要在当前目录下有`labse_onnx`文件夹，包含：
   - `model.onnx`
   - `tokenizer_config.json`
   - `vocab.txt`
   - 等tokenizer文件

2. **指定语言代码**（推荐）:
```python
from bertalign import Bertalign

aligner = Bertalign(
    src_text,
    tgt_text,
    src_lang='en',  # 指定源语言
    tgt_lang='zh',  # 指定目标语言
    is_split=True
)
```

## 原始项目

- GitHub: https://github.com/bfsujason/bertalign
- 原始版本: 0.1.0
- 修补版本: 0.1.0.post1

## 许可证

与原项目相同的许可证

## 修补者

Patrick - 2025-12-21

