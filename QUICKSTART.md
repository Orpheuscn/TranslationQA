# 快速开始

## 一键安装脚本

```bash
git clone https://github.com/Orpheuscn/TranslationQA.git
cd TranslationQA
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install patched_packages/dist/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
pip install patched_packages/dist/fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
pip install -r requirements.txt
python download_models.py
python app.py
```

然后访问: http://localhost:5001

## 为什么需要特殊的安装步骤？

本项目使用了**修补过的依赖包**来解决以下问题：

1. **bertalign_macos_patched**: 修复 macOS ARM64 上的崩溃问题
2. **fasttext_numpy2_patched**: 修复 NumPy 2.x 兼容性问题

这些修补包在所有平台上都能正常工作，不仅限于 macOS。

## 详细说明

请参考 [INSTALL.md](INSTALL.md) 获取完整的安装指南和常见问题解答。

