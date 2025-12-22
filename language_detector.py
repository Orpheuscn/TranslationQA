#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言检测模块

使用 fastText 进行语言检测
"""

import os
import urllib.request
import ssl


class LanguageDetector:
    """基于 fastText 的语言检测器"""
    
    # fastText 预训练模型 URL
    MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    MODEL_FILENAME = "lid.176.bin"
    
    def __init__(self, model_path=None):
        """
        初始化语言检测器
        
        参数:
            model_path: fastText 模型路径，如果为 None 则使用默认路径
        """
        self.model = None
        self.model_path = model_path or self._get_default_model_path()
        
        # 尝试加载 fastText
        try:
            import fasttext
            self.fasttext = fasttext
            self._load_model()
        except ImportError:
            print("⚠️  fastText 未安装")
            print("   安装命令: pip install fasttext")
            raise ImportError("fastText is required for language detection")
    
    def _get_default_model_path(self):
        """获取默认模型路径"""
        # 将模型保存在当前目录下的 models 文件夹
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(models_dir, exist_ok=True)
        return os.path.join(models_dir, self.MODEL_FILENAME)
    
    def _download_model(self):
        """下载 fastText 语言检测模型"""
        print(f"正在下载 fastText 语言检测模型...")
        print(f"URL: {self.MODEL_URL}")
        print(f"保存路径: {self.model_path}")

        try:
            # 创建一个不验证 SSL 证书的上下文（用于解决证书问题）
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # 下载模型
            with urllib.request.urlopen(self.MODEL_URL, context=ssl_context) as response:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0

                with open(self.model_path, 'wb') as f:
                    while True:
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')

                print()  # 换行
            print("✓ 模型下载成功")
        except Exception as e:
            print(f"\n✗ 模型下载失败: {e}")
            print("\n请手动下载模型:")
            print(f"  1. 访问: {self.MODEL_URL}")
            print(f"  2. 保存到: {self.model_path}")
            raise
    
    def _load_model(self):
        """加载 fastText 模型"""
        # 如果模型文件不存在，先下载
        if not os.path.exists(self.model_path):
            self._download_model()

        try:
            # 加载模型
            self.model = self.fasttext.load_model(self.model_path)
            print("✓ fastText 语言检测模型加载成功")
        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
            raise
    
    def detect(self, text, k=1):
        """
        检测文本的语言

        参数:
            text: 输入文本
            k: 返回前 k 个最可能的语言

        返回:
            如果 k=1: 返回语言代码字符串 (如 'en', 'zh', 'ja')
            如果 k>1: 返回 (语言代码列表, 概率列表) 元组
        """
        if not self.model:
            raise RuntimeError("模型未加载")

        # 预处理文本：移除换行符和多余空格
        text = text.replace('\n', ' ').strip()

        if not text:
            return 'en' if k == 1 else (['en'], [1.0])

        # fastText 预测
        predictions = self.model.predict(text, k=k)

        # predictions 返回格式: (('__label__en',), array([0.99]))
        labels, scores = predictions

        # 提取语言代码（去掉 '__label__' 前缀）
        languages = [label.replace('__label__', '') for label in labels]

        # 转换 scores 为列表（兼容新版 NumPy）
        import numpy as np
        if isinstance(scores, np.ndarray):
            scores_list = scores.tolist()
        else:
            scores_list = list(scores)

        if k == 1:
            return languages[0]
        else:
            return languages, scores_list
    
    def detect_with_confidence(self, text):
        """
        检测文本的语言并返回置信度

        参数:
            text: 输入文本

        返回:
            (language, confidence) 元组
        """
        if not self.model:
            raise RuntimeError("模型未加载")

        # 预处理文本
        text = text.replace('\n', ' ').strip()

        if not text:
            return 'en', 1.0

        # fastText 预测
        predictions = self.model.predict(text, k=1)
        labels, scores = predictions

        language = labels[0].replace('__label__', '')

        # 转换 scores 为 float（兼容新版 NumPy）
        import numpy as np
        if isinstance(scores, np.ndarray):
            confidence = float(scores[0])
        else:
            confidence = float(scores[0]) if scores else 1.0

        return language, confidence


if __name__ == "__main__":
    # 测试代码
    detector = LanguageDetector()
    
    test_texts = [
        "This is an English sentence.",
        "这是一个中文句子。",
        "これは日本語の文です。",
        "Ceci est une phrase en français.",
        "Dies ist ein deutscher Satz.",
        "Esta es una oración en español.",
    ]
    
    print("\n语言检测测试:")
    print("-" * 50)
    for text in test_texts:
        lang, conf = detector.detect_with_confidence(text)
        print(f"文本: {text}")
        print(f"语言: {lang} (置信度: {conf:.4f})\n")

