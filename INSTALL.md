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

### 5. 下载 LaBSE ONNX 模型

**LaBSE ONNX 模型**（必需，约 470MB）：

```bash
python download_models.py
```

**spaCy 语言模型**（可选，用于特定语言的分句和分词）：

```bash
# 日语（推荐，如果处理日文文本）
python -m spacy download ja_ginza

# 韩语
python -m spacy download ko_core_news_sm

# 其他语言根据需要下载
# python -m spacy download en_core_web_sm  # 英语
# python -m spacy download fr_core_news_sm  # 法语
```

### 6. 启动 Web 服务

```bash
python app.py
```

**首次启动说明**：
- fastText 语言检测模型（~125MB）会自动下载到 `models/lid.176.bin`
- HanLP 中文模型（~171MB）会自动下载到 `models/hanlp/`
- 下载过程可能需要几分钟，取决于网络速度

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

# 验证 LaBSE ONNX 模型
python -c "import os; print('✓ LaBSE ONNX 模型已下载' if os.path.exists('labse_onnx/model.onnx') else '✗ 请运行 download_models.py')"

# 验证模型配置
python model_config.py
```

## 常见问题

### Q: 为什么不直接 `pip install bertalign`？

A: 原版 `bertalign` 在 macOS ARM64 上会崩溃，必须使用修补版。

### Q: 可以在其他平台上使用吗？

A: 可以。修补版在所有平台上都能正常工作，不仅限于 macOS ARM64。

### Q: 模型文件太大怎么办？

A: 程序使用的模型总计约 766MB：
- LaBSE ONNX: ~470MB（必需，需手动下载）
- fastText: ~125MB（首次运行时自动下载）
- HanLP: ~171MB（首次使用中文时自动下载）

如果网络不好，可以尝试：
- LaBSE 模型：使用国内镜像或手动下载后放到 `labse_onnx/` 目录
- 其他模型：首次运行时会自动下载，如果失败会提示手动下载链接

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
rm -rf venv/              # 虚拟环境和 spaCy 模型
rm -rf labse_onnx/        # LaBSE ONNX 模型 (~470MB)
rm -rf models/            # fastText 和 HanLP 模型 (~296MB)
```

## 技术支持

如有问题，请在 GitHub 上提交 Issue:
https://github.com/Orpheuscn/TranslationQA/issues

