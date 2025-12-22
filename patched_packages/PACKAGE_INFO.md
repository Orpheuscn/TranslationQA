# 修补版Python包详细信息

## 📦 包信息总览

### Bertalign (macOS ARM64修补版)

| 属性 | 值 |
|------|-----|
| **包名** | bertalign-macos-patched |
| **原始版本** | 0.1.0 |
| **修补版本** | 0.1.0.post1 |
| **原始项目** | https://github.com/bfsujason/bertalign |
| **修补日期** | 2025-12-21 |
| **修补者** | Patrick |
| **文件格式** | .whl (13KB), .tar.gz (13KB) |

**修改的文件**:
1. `bertalign/encoder.py` - 完全重写 (+52行, -24行)
2. `bertalign/aligner.py` - 添加参数 (+8行, -2行)
3. `bertalign/corelib.py` - 修复bug (+18行, -3行)

**修复的问题**:
1. ✅ SentenceTransformer在macOS ARM64上导致Segmentation Fault崩溃
2. ✅ Google Translate API调用超时问题
3. ✅ FAISS批量搜索在macOS ARM64上挂起

**技术方案**:
1. 使用ONNX Runtime替代SentenceTransformer加载LaBSE模型
2. 添加`src_lang`和`tgt_lang`可选参数，避免自动语言检测
3. 使用逐个搜索替代FAISS批量搜索

---

### FastText (NumPy 2.x兼容性修补版)

| 属性 | 值 |
|------|-----|
| **包名** | fasttext-numpy2-patched |
| **原始版本** | 0.9.3 |
| **修补版本** | 0.9.3.post1 |
| **原始项目** | https://github.com/facebookresearch/fastText |
| **修补日期** | 2025-12-21 |
| **修补者** | Patrick |
| **文件格式** | .whl (18KB), .tar.gz (16KB) |

**修改的文件**:
1. `fasttext/FastText.py` - 修改1行（第239行）

**修复的问题**:
1. ✅ `np.array(probs, copy=False)`在NumPy 2.x中已被弃用

**技术方案**:
1. 将`np.array(probs, copy=False)`改为`np.asarray(probs)`

---

## 🔧 技术细节

### Bertalign修改详情

#### 1. encoder.py - ONNX支持

**原始代码**:
```python
from sentence_transformers import SentenceTransformer

class Encoder:
    def __init__(self, model="LaBSE"):
        self.model = SentenceTransformer(model)
    
    def transform(self, sents):
        return self.model.encode(sents)
```

**修改后代码**:
```python
import onnxruntime as ort
from transformers import AutoTokenizer

USE_ONNX = True

class Encoder:
    def __init__(self, model="labse_onnx"):
        if USE_ONNX:
            self.session = ort.InferenceSession(f"{model}/model.onnx")
            self.tokenizer = AutoTokenizer.from_pretrained(model)
    
    def encode_onnx(self, texts):
        # ONNX推理逻辑
        ...
    
    def transform(self, sents):
        if USE_ONNX:
            return self.encode_onnx(sents)
```

#### 2. aligner.py - 语言参数

**原始代码**:
```python
def __init__(self, src, tgt, ...):
    src_lang = detect_lang(src)  # 调用Google Translate API
    tgt_lang = detect_lang(tgt)
```

**修改后代码**:
```python
def __init__(self, src, tgt, src_lang=None, tgt_lang=None, ...):
    if src_lang is None:
        src_lang = detect_lang(src)
    if tgt_lang is None:
        tgt_lang = detect_lang(tgt)
```

#### 3. corelib.py - FAISS修复

**原始代码**:
```python
def find_top_k_sents(src_vecs, index, k):
    D, I = index.search(src_vecs, k)  # 批量搜索会挂起
    return D, I
```

**修改后代码**:
```python
def find_top_k_sents(src_vecs, index, k):
    n_src = src_vecs.shape[0]
    D = np.zeros((n_src, k), dtype=np.float32)
    I = np.zeros((n_src, k), dtype=np.int64)
    
    # 逐个搜索避免挂起
    for i in range(n_src):
        query = src_vecs[i:i+1, :]
        d, idx = index.search(query, k)
        D[i] = d[0]
        I[i] = idx[0]
    
    return D, I
```

### FastText修改详情

**原始代码** (第239行):
```python
return labels, np.array(probs, copy=False)
```

**修改后代码** (第239行):
```python
return labels, np.asarray(probs)
```

---

## 📋 依赖要求

### Bertalign修补版

```
numpy>=1.19.0
faiss-cpu>=1.7.0
onnxruntime>=1.10.0
transformers>=4.0.0
```

### FastText修补版

```
numpy>=1.19.0
pybind11>=2.2
```

---

## 🎯 使用示例

### Bertalign使用示例

```python
from bertalign import Bertalign

# 准备文本
src_text = ["Hello world.", "How are you?"]
tgt_text = ["你好世界。", "你好吗？"]

# 创建对齐器（推荐指定语言）
aligner = Bertalign(
    src_text,
    tgt_text,
    src_lang='en',  # 指定源语言
    tgt_lang='zh',  # 指定目标语言
    is_split=True
)

# 获取对齐结果
alignments = aligner.align_sents()
```

### FastText使用示例

```python
import fasttext

# 使用方法与原版完全相同
model = fasttext.load_model('model.bin')
predictions = model.predict(text)
```

---

## 📄 文件清单

```
dist/
├── bertalign_macos_patched-0.1.0.post1-py3-none-any.whl    # Bertalign wheel包
├── bertalign_macos_patched-0.1.0.post1.tar.gz              # Bertalign源码包
├── fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl    # FastText wheel包
└── fasttext_numpy2_patched-0.9.3.post1.tar.gz              # FastText源码包
```

---

**创建日期**: 2025-12-21  
**维护者**: Patrick  
**详细修改记录**: 参见项目根目录的`虚拟环境修改记录.md`

