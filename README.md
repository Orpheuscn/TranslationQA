# TranslationQA - 翻译质量检查工具

基于深度学习的翻译质量检查工具，支持自动句子对齐、语义相似度计算、翻译异常检测等功能。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)

## ✨ 主要特性

- **智能句子对齐**: 使用 Bertalign 实现 N:M 复杂对齐
- **语义相似度计算**: 基于 LaBSE ONNX 模型（768维向量）
- **翻译异常检测**: 自动检测缺失、增添、相似度低三种异常
- **多语言支持**: 支持中英日韩等多种语言，使用 spaCy/HanLP 高质量分句
- **Web 界面**: 直观的网页界面，支持批量处理和报告导出
- **本地运行**: 所有模型本地加载，无需联网（安装后）

## 🚀 一键安装（推荐）

```bash
git clone https://github.com/Orpheuscn/TranslationQA.git
cd TranslationQA
chmod +x install.sh
./install.sh
```

安装脚本会自动完成：
- 创建 Python 虚拟环境
- 安装所有依赖（包括修补版 bertalign 和 fasttext-wheel）
- 下载 LaBSE ONNX 模型（~1.8GB）
- 下载 spaCy 语言模型（英语、中文、日语、法语、德语、西班牙语）
- 配置环境变量（修复 OpenMP 冲突）

## 📦 手动安装

如果一键安装失败，可以手动执行：

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装修补版依赖
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    dist/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    ./patched_packages/fasttext-patched

# 3. 安装其他依赖
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r requirements.txt

# 4. 下载 LaBSE 模型
python download_models.py  # 需要输入 'y' 确认

# 5. 下载 spaCy 模型（可选）
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ja-ginza
```

## 🎯 启动应用

```bash
source venv/bin/activate
python app.py
```

然后访问: http://localhost:5001

或者双击 `start_server.command`（macOS）

## 🔧 依赖说明

### 核心依赖
- `numpy>=1.24.0,<2.0` - 数值计算（fasttext 要求 < 2.0）
- `pandas>=2.0.0` - 数据处理
- `onnxruntime>=1.15.0` - ONNX 模型推理
- `transformers>=4.30.0` - Hugging Face 模型

### 修补版依赖
- `bertalign-macos-patched` - 已移除 googletrans 和 sentence_splitter
  - 不再依赖 Google Translate API
  - 使用 fastText 进行语言检测
  - 使用项目自带的 spaCy/HanLP 进行分句
- `fasttext-wheel` - 官方 fastText，包含预编译的 C++ 扩展

### Web 服务
- `flask>=3.0.0` - Web 框架
- `flask-cors>=4.0.0` - 跨域支持

### NLP 工具
- `spacy>=3.7.0` - 高级分句和 NLP
- `hanlp>=2.1.0` - 中文处理
- spaCy 语言模型（自动安装）：
  - `en_core_web_sm` - 英语
  - `zh_core_web_sm` - 中文
  - `ja_ginza` - 日语（Ginza）
  - `fr_core_news_sm` - 法语
  - `de_core_news_sm` - 德语
  - `es_core_news_sm` - 西班牙语

### 模型文件（自动下载）
- **LaBSE ONNX** (~1.8GB) - 语义嵌入，手动下载
- **fastText** (~125MB) - 语言检测，首次运行自动下载
- **HanLP** (~171MB) - 中文分句，首次使用中文时自动下载

## 📁 项目结构

```
TranslationQA/
├── install.sh                    # 一键安装脚本
├── start_server.command          # 启动脚本（macOS）
├── requirements.txt              # Python 依赖
├── dist/                         # 预构建的 wheel 包
│   └── bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
├── patched_packages/             # 修补包源码
│   ├── bertalign-patched/        # 已移除 googletrans
│   └── fasttext-patched/         # NumPy 2.x 兼容
├── labse_onnx/                   # LaBSE ONNX 模型（需下载）
├── models/                       # 其他模型（自动下载）
├── static/                       # Web 前端
├── templates/                    # HTML 模板
└── *.py                          # Python 源码
```

## 🛠️ 主要改进（v0.1.1）

1. **移除不必要的依赖**
   - ❌ googletrans - 不再依赖 Google Translate API
   - ❌ sentence_splitter - 使用更高级的 spaCy/HanLP

2. **完善的依赖管理**
   - 所有依赖都在 requirements.txt 中明确列出
   - 预构建的 wheel 包加快安装速度

3. **一键安装脚本**
   - 自动化所有安装步骤
   - 智能检测已安装的组件

4. **向后兼容**
   - TranslationQA 代码无需修改
   - 使用 fastText 替代 Google Translate 进行语言检测
   - 使用 spaCy/HanLP 进行高质量分句

## 📊 使用方法

### Web 界面
1. 启动服务器后访问 http://localhost:5001
2. 在文本框中输入原文和译文
3. 点击"开始检查"按钮
4. 查看对齐结果和检测到的异常
5. 导出 CSV 或 JSON 报告

### Python API
```python
from translation_qa_tool import TranslationQA

# 初始化
qa = TranslationQA(
    similarity_threshold=0.7,      # 相似度阈值
    force_split_threshold=0.5,     # 强制拆散阈值
    max_align=6                    # 最大对齐数
)

# 检查翻译
results = qa.check_translation(
    source_text="Your source text here.",
    target_text="你的译文在这里。",
    source_language='en',
    target_language='zh'
)

# 导出报告
qa.export_csv(results, 'report.csv')
```

## ⚠️ 常见问题

### 1. 安装时 SSL 证书错误
使用 `--trusted-host` 参数：
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ...
```

### 2. LaBSE 模型下载失败
手动下载：
- 访问: https://huggingface.co/sentence-transformers/LaBSE
- 下载 `onnx/model.onnx`, `tokenizer.json`, `vocab.txt`
- 放到 `labse_onnx/` 目录

### 3. 端口 5001 被占用
修改 `app.py` 中的端口号，或者先停止占用端口的进程：
```bash
lsof -ti:5001 | xargs kill -9
```

### 4. .cache 文件夹是什么？
- 由 huggingface_hub 自动创建的缓存目录
- 可以安全删除（会重新下载）
- 已添加到 .gitignore

## 🎯 技术栈

- **句子对齐**: Bertalign 1.1.0（已修补）
- **语义嵌入**: LaBSE ONNX（768维）
- **相似度计算**: 余弦相似度
- **分句工具**: spaCy / HanLP / 简单规则
- **语言检测**: fastText
- **Web 框架**: Flask
- **前端**: HTML + CSS + JavaScript

## 📝 许可

MIT License

## 🙏 致谢

- [Bertalign](https://github.com/bfsujason/bertalign) - 句子对齐算法
- [LaBSE](https://huggingface.co/sentence-transformers/LaBSE) - 多语言语义嵌入模型
- [ONNX Runtime](https://onnxruntime.ai/) - 高性能推理引擎
- [spaCy](https://spacy.io/) - 工业级 NLP 工具
- [HanLP](https://hanlp.hankcs.com/) - 中文 NLP 工具

## 📮 联系方式

如有问题或建议，请在 [GitHub Issues](https://github.com/Orpheuscn/TranslationQA/issues) 中提出。
