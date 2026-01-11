#!/bin/bash
# TranslationQA 一键安装脚本
# 安装所有依赖和模型

set -e  # 遇到错误立即退出

echo "================================================================================"
echo "TranslationQA 一键安装脚本"
echo "================================================================================"
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3，请先安装 Python 3.12+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python 版本: $PYTHON_VERSION"
echo ""

# 步骤 1: 创建虚拟环境
echo "步骤 1/8: 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
fi
echo ""

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"
echo ""

# 步骤 2: 升级 pip
echo "步骤 2/8: 升级 pip..."
pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
echo ""

# 步骤 3: 安装修补版 bertalign
echo "步骤 3/8: 安装修补版 bertalign..."
if [ -f "dist/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl" ]; then
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org dist/bertalign_macos_patched-0.1.0.post1-py3-none-any.whl
else
    echo "  ⚠️  未找到预构建的 wheel，从源码安装..."
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ./patched_packages/bertalign-patched
fi
echo "✓ bertalign-macos-patched 安装完成"
echo ""

# 步骤 4: 安装 fasttext（使用官方 wheel 版本）
echo "步骤 4/8: 安装 fasttext..."
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org fasttext-wheel
echo "✓ fasttext-wheel 安装完成"
echo ""

# 步骤 5: 安装其他依赖
echo "步骤 5/8: 安装其他依赖..."
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
echo "✓ 依赖安装完成"
echo ""

# 步骤 6: 下载 LaBSE ONNX 模型
echo "步骤 6/8: 下载 LaBSE ONNX 模型..."
if [ -f "labse_onnx/model.onnx" ]; then
    echo "⚠️  LaBSE ONNX 模型已存在，跳过下载"
else
    echo "开始下载 LaBSE ONNX 模型（约 1.8GB）..."
    python -c "
from download_models import download_from_huggingface
success = download_from_huggingface()
if not success:
    print('❌ LaBSE 模型下载失败')
    exit(1)
"
    echo "✓ LaBSE ONNX 模型下载完成"
fi
echo ""

# 步骤 7: 下载 spaCy 语言模型
echo "步骤 7/8: 下载 spaCy 语言模型..."
echo ""

# 英语（常用）
echo "  下载英语模型（en_core_web_sm）..."
if python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "    ✓ en_core_web_sm 已安装，跳过"
else
    python -m spacy download en_core_web_sm --trusted-host pypi.org --trusted-host files.pythonhosted.org
    echo "    ✓ en_core_web_sm 安装完成"
fi
echo ""

# 中文使用 HanLP，不需要 spaCy 模型

# 日语（ginza）
echo "  下载日语模型（ja_ginza）..."
if python -c "import spacy; spacy.load('ja_ginza')" 2>/dev/null; then
    echo "    ✓ ja_ginza 已安装，跳过"
else
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ja-ginza
    echo "    ✓ ja_ginza 安装完成"
fi
echo ""

# 法语（常用）
echo "  下载法语模型（fr_core_news_sm）..."
if python -c "import spacy; spacy.load('fr_core_news_sm')" 2>/dev/null; then
    echo "    ✓ fr_core_news_sm 已安装，跳过"
else
    python -m spacy download fr_core_news_sm --trusted-host pypi.org --trusted-host files.pythonhosted.org
    echo "    ✓ fr_core_news_sm 安装完成"
fi
echo ""

# 德语（常用）
echo "  下载德语模型（de_core_news_sm）..."
if python -c "import spacy; spacy.load('de_core_news_sm')" 2>/dev/null; then
    echo "    ✓ de_core_news_sm 已安装，跳过"
else
    python -m spacy download de_core_news_sm --trusted-host pypi.org --trusted-host files.pythonhosted.org
    echo "    ✓ de_core_news_sm 安装完成"
fi
echo ""

# 西班牙语（常用）
echo "  下载西班牙语模型（es_core_news_sm）..."
if python -c "import spacy; spacy.load('es_core_news_sm')" 2>/dev/null; then
    echo "    ✓ es_core_news_sm 已安装，跳过"
else
    python -m spacy download es_core_news_sm --trusted-host pypi.org --trusted-host files.pythonhosted.org
    echo "    ✓ es_core_news_sm 安装完成"
fi
echo ""

echo "✓ 所有模型下载完成"
echo ""

# 步骤 8: 设置环境变量（修复 OpenMP 冲突）
echo "步骤 8/8: 配置环境变量..."
ACTIVATE_SCRIPT="venv/bin/activate"
if ! grep -q "KMP_DUPLICATE_LIB_OK" "$ACTIVATE_SCRIPT"; then
    cat >> "$ACTIVATE_SCRIPT" << 'ENVEOF'

# 修复 OpenMP 运行时冲突
export KMP_DUPLICATE_LIB_OK=TRUE
ENVEOF
    echo "✓ 已添加 KMP_DUPLICATE_LIB_OK=TRUE 到 activate 脚本"
else
    echo "⚠️  环境变量已设置，跳过"
fi
echo ""

# 完成
echo "================================================================================"
echo "✅ 安装完成！"
echo "================================================================================"
echo ""
echo "已安装的组件："
echo "  ✓ bertalign-macos-patched（已移除 googletrans 和 sentence_splitter 依赖）"
echo "  ✓ fasttext-wheel（语言检测，包含预编译二进制）"
echo "  ✓ LaBSE ONNX 模型（~1.8GB）"
echo "  ✓ spaCy 模型："
echo "    - 英语 (en_core_web_sm)"
echo "    - 中文 (zh_core_web_sm)"
echo "    - 日语 (ja_ginza)"
echo "    - 法语 (fr_core_news_sm)"
echo "    - 德语 (de_core_news_sm)"
echo "    - 西班牙语 (es_core_news_sm)"
echo ""
echo "首次启动说明："
echo "  - fastText 语言检测模型（~125MB）会在首次运行时自动下载"
echo "  - HanLP 中文模型（~171MB）会在首次使用中文时自动下载"
echo ""
echo "启动服务器："
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "然后访问: http://localhost:5001"
echo ""
