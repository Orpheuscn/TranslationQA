#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型路径配置模块

统一管理所有模型的路径配置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# models 文件夹
MODELS_DIR = PROJECT_ROOT / "models"

# ===== LaBSE ONNX 模型 =====
LABSE_ONNX_DIR = PROJECT_ROOT / "labse_onnx"

# ===== fastText 语言检测模型 =====
FASTTEXT_MODEL_PATH = MODELS_DIR / "lid.176.bin"

# ===== HanLP 模型路径配置 =====
# 优先使用本地模型，如果不存在则使用系统缓存
HANLP_LOCAL_DIR = MODELS_DIR / "hanlp"

def get_hanlp_home():
    """
    获取 HanLP 模型目录
    
    优先级：
    1. 环境变量 HANLP_HOME
    2. 项目本地 models/hanlp/
    3. 系统默认 ~/.hanlp/
    
    返回:
        Path: HanLP 模型目录路径
    """
    # 1. 检查环境变量
    if 'HANLP_HOME' in os.environ:
        return Path(os.environ['HANLP_HOME'])
    
    # 2. 检查项目本地目录
    if HANLP_LOCAL_DIR.exists():
        return HANLP_LOCAL_DIR
    
    # 3. 使用系统默认目录
    return Path.home() / ".hanlp"

def setup_hanlp_env():
    """
    设置 HanLP 环境变量
    
    强制使用项目本地 models/hanlp/ 目录
    """
    # 确保目录存在
    HANLP_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # 强制设置为本地目录
    os.environ['HANLP_HOME'] = str(HANLP_LOCAL_DIR.absolute())
    print(f"✓ 使用本地 HanLP 目录: {HANLP_LOCAL_DIR}")
    return True

# ===== 模型信息 =====
def get_models_info():
    """
    获取所有模型的信息
    
    返回:
        dict: 模型信息字典
    """
    info = {
        'labse_onnx': {
            'path': LABSE_ONNX_DIR,
            'exists': LABSE_ONNX_DIR.exists(),
            'description': 'LaBSE ONNX 句子编码模型'
        },
        'fasttext': {
            'path': FASTTEXT_MODEL_PATH,
            'exists': FASTTEXT_MODEL_PATH.exists(),
            'description': 'fastText 语言检测模型'
        },
        'hanlp': {
            'path': get_hanlp_home(),
            'exists': get_hanlp_home().exists(),
            'description': 'HanLP 中文分词/分句模型',
            'is_local': get_hanlp_home() == HANLP_LOCAL_DIR
        }
    }
    return info

def print_models_info():
    """打印所有模型的信息"""
    info = get_models_info()
    
    print("\n" + "="*60)
    print("📦 模型配置信息")
    print("="*60)
    
    for name, details in info.items():
        status = "✅ 已加载" if details['exists'] else "❌ 缺失"
        location = "本地" if details.get('is_local', True) else "系统缓存"
        
        print(f"\n{details['description']}:")
        print(f"  路径: {details['path']}")
        print(f"  状态: {status}")
        if 'is_local' in details:
            print(f"  位置: {location}")

if __name__ == "__main__":
    # 测试
    print_models_info()
