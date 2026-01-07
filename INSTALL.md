# 安装指南

## 系统要求

- Python 3.12+
- macOS / Linux / Windows
- 至少 4GB 可用磁盘空间（用于模型文件）

## 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/Orpheuscn/TranslationQA.git
cd TranslationQA
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装修补过的依赖包

**重要**: 本项目使用了修补过的 `bertalign` 和 `fasttext` 包，必须先安装这些包：

```bash
# 安装修补版 bertalign（修复 macOS ARM64 兼容性问题）
pip install patched_packages/dist/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl

# 安装修补版 fasttext（修复 NumPy 2.x 兼容性问题）
pip install patched_packages/dist/fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
```

### 4. 安装其他依赖

```bash
pip install -r requirements.txt
```

### 5. 下载模型文件

**LaBSE ONNX 模型**（必需，约 1.8GB）：

```bash
python download_models.py
```

**spaCy 韩语模型**（可选）：

```bash
python -m spacy download ko_core_news_sm
```

### 6. 启动 Web 服务

```bash
python app.py
```

然后在浏览器中访问: http://localhost:5001

## 为什么需要修补版的包？

### bertalign_macos_patched

原版 `bertalign` 在 macOS ARM64 上存在以下问题：
1. **SentenceTransformer 崩溃**: 使用 ONNX Runtime 替代
2. **Google Translate API 超时**: 添加语言参数选项
3. **FAISS 批量搜索挂起**: 使用逐个搜索的 workaround

### fasttext_numpy2_patched

原版 `fasttext` 在 NumPy 2.x 上存在兼容性问题：
- 修复 `np.array(copy=False)` 弃用警告

详细修改说明请参考项目根目录的 `虚拟环境修改记录.md`（仅在源码中可见）。

## 验证安装

```bash
# 验证 Python 包
python -c "import bertalign; import fasttext; print('✓ 修补包安装成功')"

# 验证 ONNX 模型
python -c "import os; print('✓ ONNX 模型已下载' if os.path.exists('labse_onnx/model.onnx') else '✗ 请运行 download_models.py')"
```

## 常见问题

### Q: 为什么不直接 `pip install bertalign`？

A: 原版 `bertalign` 在 macOS ARM64 上会崩溃，必须使用修补版。

### Q: 可以在其他平台上使用吗？

A: 可以。修补版在所有平台上都能正常工作，不仅限于 macOS ARM64。

### Q: 模型文件太大怎么办？

A: 模型文件约 1.8GB，是必需的。如果网络不好，可以尝试：
- 使用国内镜像（如果 `download_models.py` 支持）
- 手动下载后放到 `labse_onnx/` 目录

### Q: 如何更新依赖？

A: 不建议更新 `bertalign` 和 `fasttext`，其他依赖可以正常更新：

```bash
pip install --upgrade flask flask-cors transformers
```

## 开发模式

如果你需要修改源代码：

```bash
# 安装开发依赖
pip install -e .

# 运行测试
python -m pytest tests/
```

## 卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境和模型文件
rm -rf venv/
rm -rf labse_onnx/
rm -rf models/
```

## 技术支持

如有问题，请在 GitHub 上提交 Issue:
https://github.com/Orpheuscn/TranslationQA/issues

