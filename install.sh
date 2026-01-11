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
echo "下载 fastText 语言检测模型（lid.176.bin, ~125MB）..."
python -c "
from language_detector import LanguageDetector
detector = LanguageDetector()
if detector.is_available():
    print('✓ fastText 语言检测模型下载完成')
else:
    print('⚠️  fastText 模型下载失败，将在首次运行时重试')
"
echo ""

# 步骤 5: 安装其他依赖
echo "步骤 5/8: 安装其他依赖..."
# 先安装 NumPy < 2.0（fasttext 要求）
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org 'numpy>=1.24.0,<2.0'
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

# 定义所有需要安装的语言模型（除了中文使用 HanLP）
# 格式：language_code:model_name
MODELS=(
    "en:en_core_web_sm"      # 英语
    "ja:ja_ginza"            # 日语（Ginza）
    "fr:fr_core_news_sm"     # 法语
    "de:de_core_news_sm"     # 德语
    "es:es_core_news_sm"     # 西班牙语
    "it:it_core_news_sm"     # 意大利语
    "pt:pt_core_news_sm"     # 葡萄牙语
    "nl:nl_core_news_sm"     # 荷兰语
    "el:el_core_news_sm"     # 希腊语
    "pl:pl_core_news_sm"     # 波兰语
    "ru:ru_core_news_sm"     # 俄语
    "ko:ko_core_news_sm"     # 韩语
)

# 安装所有模型
for item in "${MODELS[@]}"; do
    lang="${item%%:*}"
    model="${item##*:}"
    
    echo "  下载 ${lang} 模型（${model}）..."
    
    if python -c "import spacy; spacy.load('${model}')" 2>/dev/null; then
        echo "    ✓ ${model} 已安装，跳过"
    else
        if [ "$model" = "ja_ginza" ]; then
            # ja_ginza 需要特殊安装
            pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ja-ginza
        else
            python -m spacy download ${model} --trusted-host pypi.org --trusted-host files.pythonhosted.org
        fi
        echo "    ✓ ${model} 安装完成"
    fi
    echo ""
done

echo "✓ 所有 spaCy 模型下载完成"
echo ""

# 步骤 8: 配置环境变量和 HanLP
echo "步骤 8/8: 配置环境变量和 HanLP..."

# 设置 HanLP 使用本地目录
mkdir -p models/hanlp
export HANLP_HOME="$(pwd)/models/hanlp"

# 添加环境变量到 activate 脚本
ACTIVATE_SCRIPT="venv/bin/activate"
if ! grep -q "HANLP_HOME" "$ACTIVATE_SCRIPT"; then
    cat >> "$ACTIVATE_SCRIPT" << 'ENVEOF'

# 项目环境变量
export HANLP_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/models/hanlp"
export KMP_DUPLICATE_LIB_OK=TRUE
ENVEOF
    echo "✓ 已添加环境变量到 activate 脚本"
else
    echo "⚠️  环境变量已设置，跳过"
fi

# 预初始化 HanLP（规则分句器不需要下载模型）
echo ""
echo "预初始化 HanLP（规则分句器，无需下载模型）..."
python -c "
import os
os.environ['HANLP_HOME'] = '$(pwd)/models/hanlp'
try:
    from hanlp.utils.rules import split_sentence
    # 测试一下
    result = list(split_sentence('这是测试。'))
    print('✓ HanLP 规则分句器初始化成功')
    print('  说明：规则分句器不需要下载模型文件')
except Exception as e:
    print(f'⚠️  HanLP 初始化失败: {e}')
"
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
echo "  ✓ HanLP 规则分句器（中文，无需模型文件）"
echo "  ✓ spaCy 模型（12种语言）："
echo "    - 英语、日语、法语、德语、西班牙语、意大利语"
echo "    - 葡萄牙语、荷兰语、希腊语、波兰语、俄语、韩语"
echo ""
echo "环境变量："
echo "  ✓ HANLP_HOME=$(pwd)/models/hanlp"
echo "  ✓ KMP_DUPLICATE_LIB_OK=TRUE"
echo ""
echo "启动服务器："
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "然后访问: http://localhost:5001"
echo ""
