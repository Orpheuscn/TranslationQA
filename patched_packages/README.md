# 修补版Python包分发文件

本目录包含针对macOS ARM64平台修复的Python包，可以直接分享给其他用户使用。

## 📦 包含的包

### 1. Bertalign (macOS ARM64修补版)
- **文件名**: `bertalign_macos_patched-0.1.0.post1`
- **原始版本**: 0.1.0
- **修补版本**: 0.1.0.post1
- **文件大小**: ~13KB

**修复内容**:
1. ✅ 使用ONNX Runtime替代SentenceTransformer（修复macOS ARM64崩溃）
2. ✅ 添加语言参数避免Google Translate API超时
3. ✅ 修复FAISS批量搜索在macOS ARM64上的挂起问题

### 2. FastText (NumPy 2.x兼容性修补版)
- **文件名**: `fasttext_numpy2_patched-0.9.3.post1`
- **原始版本**: 0.9.3
- **修补版本**: 0.9.3.post1
- **文件大小**: ~16-18KB

**修复内容**:
1. ✅ 修复NumPy 2.x兼容性问题（`np.array(copy=False)` → `np.asarray()`）

## 📥 安装方法

### 方法1: 使用wheel文件（推荐）

```bash
# 安装bertalign修补版
pip install bertalign_macos_patched-0.1.0.post1-py3-none-any.whl

# 安装fasttext修补版
pip install fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
```

### 方法2: 使用tar.gz文件

```bash
# 安装bertalign修补版
pip install bertalign_macos_patched-0.1.0.post1.tar.gz

# 安装fasttext修补版
pip install fasttext_numpy2_patched-0.9.3.post1.tar.gz
```

### 方法3: 从URL安装（如果文件已上传到服务器）

```bash
pip install https://your-server.com/path/to/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
pip install https://your-server.com/path/to/fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
```

## ⚠️ 重要说明

### Bertalign使用注意事项

1. **需要ONNX模型文件**:
   - 修补版使用ONNX Runtime，需要LaBSE的ONNX模型
   - 模型文件应放在当前工作目录的`labse_onnx`文件夹中
   - 包含文件: `model.onnx`, `tokenizer_config.json`, `vocab.txt`等

2. **推荐指定语言代码**:
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

3. **依赖要求**:
   - numpy >= 1.19.0
   - faiss-cpu >= 1.7.0
   - onnxruntime >= 1.10.0
   - transformers >= 4.0.0

### FastText使用注意事项

1. **仅包含Python代码**:
   - 此修补版仅包含Python代码修复
   - 不包含C++编译的二进制文件
   - 如需完整功能，请确保已安装原版fasttext的二进制依赖

2. **依赖要求**:
   - numpy >= 1.19.0
   - pybind11 >= 2.2

## 🔄 卸载原版并安装修补版

```bash
# 卸载原版bertalign（如果已安装）
pip uninstall bertalign -y

# 安装修补版
pip install bertalign_macos_patched-0.1.0.post1-py3-none-any.whl

# 卸载原版fasttext（如果已安装）
pip uninstall fasttext -y

# 安装修补版
pip install fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
```

## 📂 目录结构

```
patched_packages/
├── README.md                          # 本文件
├── dist/                              # 分发文件目录
│   ├── bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
│   ├── bertalign_macos_patched-0.1.0.post1.tar.gz
│   ├── fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
│   └── fasttext_numpy2_patched-0.9.3.post1.tar.gz
├── bertalign-patched/                 # bertalign源代码和构建文件
│   ├── setup.py
│   ├── README.md
│   └── bertalign/
└── fasttext-patched/                  # fasttext源代码和构建文件
    ├── setup.py
    ├── README.md
    └── fasttext/
```

## ✅ 验证安装

```bash
# 验证bertalign
python -c "import bertalign; print('Bertalign安装成功')"

# 验证fasttext
python -c "import fasttext; print('FastText安装成功')"
```

## 📝 修改历史

| 日期 | 包名 | 版本 | 修改内容 |
|------|------|------|---------|
| 2025-12-21 | bertalign | 0.1.0.post1 | macOS ARM64兼容性修复 |
| 2025-12-21 | fasttext | 0.9.3.post1 | NumPy 2.x兼容性修复 |

## 📧 联系方式

- 修补者: Patrick
- 修补日期: 2025-12-21
- 详细修改记录: 参见项目根目录的`虚拟环境修改记录.md`

## 📄 许可证

这些修补版本遵循原项目的许可证:
- Bertalign: 原项目许可证
- FastText: MIT License

