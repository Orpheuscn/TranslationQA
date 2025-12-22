#!/bin/bash

# 修补版Python包安装脚本
# 作者: Patrick
# 日期: 2025-12-21

set -e  # 遇到错误立即退出

echo "=========================================="
echo "修补版Python包安装脚本"
echo "=========================================="
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo "建议在虚拟环境中安装，是否继续？(y/n)"
    read -r response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        echo "安装已取消"
        exit 0
    fi
fi

echo "当前Python版本:"
python --version
echo ""

# 进入dist目录
cd "$(dirname "$0")/dist"

echo "=========================================="
echo "1. 安装 Bertalign (macOS ARM64修补版)"
echo "=========================================="
echo ""

# 检查是否已安装bertalign
if pip show bertalign >/dev/null 2>&1; then
    echo "检测到已安装原版bertalign，是否卸载？(y/n)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo "卸载原版bertalign..."
        pip uninstall bertalign -y
    fi
fi

echo "安装bertalign修补版..."
pip install bertalign_macos_patched-0.1.0.post1-py3-none-any.whl

echo ""
echo "=========================================="
echo "2. 安装 FastText (NumPy 2.x兼容性修补版)"
echo "=========================================="
echo ""

# 检查是否已安装fasttext
if pip show fasttext >/dev/null 2>&1; then
    echo "检测到已安装原版fasttext，是否卸载？(y/n)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo "卸载原版fasttext..."
        pip uninstall fasttext -y
    fi
fi

echo "安装fasttext修补版..."
pip install fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl

echo ""
echo "=========================================="
echo "3. 验证安装"
echo "=========================================="
echo ""

echo "验证bertalign..."
if python -c "import bertalign; print('✅ Bertalign安装成功')" 2>/dev/null; then
    echo "Bertalign验证通过"
else
    echo "❌ Bertalign验证失败"
fi

echo ""
echo "验证fasttext..."
if python -c "import fasttext; print('✅ FastText安装成功')" 2>/dev/null; then
    echo "FastText验证通过"
else
    echo "❌ FastText验证失败"
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "⚠️  重要提示:"
echo "1. Bertalign需要ONNX模型文件（labse_onnx目录）"
echo "2. 使用时建议指定语言代码（src_lang, tgt_lang）"
echo "3. 详细使用说明请参见README.md"
echo ""

