#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本分句模块

支持多语言分句：
- 中文：使用 HanLP
- 日文：使用 GiNZA (spaCy)
- 其他语言：使用对应的 spaCy 模型
"""

import re
from language_detector import LanguageDetector
from model_config import setup_hanlp_env

# 设置 HanLP 环境变量（使用本地模型）
setup_hanlp_env()


class TextSplitter:
    """多语言文本分句器"""

    # 语言代码到 spaCy 模型的映射
    SPACY_MODELS = {
        'en': 'en_core_web_sm',      # 英语
        'fr': 'fr_core_news_sm',     # 法语
        'de': 'de_core_news_sm',     # 德语
        'es': 'es_core_news_sm',     # 西班牙语
        'it': 'it_core_news_sm',     # 意大利语
        'pt': 'pt_core_news_sm',     # 葡萄牙语
        'nl': 'nl_core_news_sm',     # 荷兰语
        'el': 'el_core_news_sm',     # 希腊语
        'fi': 'fi_core_news_sm',     # 芬兰语
        'sv': 'sv_core_news_sm',     # 瑞典语
        'da': 'da_core_news_sm',     # 丹麦语
        'ru': 'ru_core_news_sm',     # 俄语
        'ja': 'ja_ginza',            # 日语 (GiNZA)
        'ko': 'ko_core_news_sm',     # 韩语
    }

    def __init__(self, auto_detect=True):
        """
        初始化分句器

        参数:
            auto_detect: 是否自动检测语言（使用 fastText）
        """
        self.auto_detect = auto_detect
        self.language_detector = None
        self.spacy_models = {}  # 缓存已加载的 spaCy 模型
        self.hanlp_split_sentence = None

        # 初始化语言检测器
        if auto_detect:
            try:
                self.language_detector = LanguageDetector()
            except ImportError:
                print("⚠️  语言检测器初始化失败，将使用手动指定语言")
                self.auto_detect = False

        # 尝试加载 HanLP 的规则分句器（用于中文）
        try:
            from hanlp.utils.rules import split_sentence
            self.hanlp_split_sentence = split_sentence
            print("✓ HanLP 规则分句器加载成功")
        except ImportError:
            print("⚠️  HanLP 未安装，中文将使用简单规则分句")
            print("   安装命令: pip install hanlp")

    def _load_spacy_model(self, language):
        """
        加载指定语言的 spaCy 模型

        参数:
            language: 语言代码 (如 'en', 'fr', 'ja')

        返回:
            spaCy nlp 对象，如果加载失败则返回 None
        """
        # 如果已经加载过，直接返回
        if language in self.spacy_models:
            return self.spacy_models[language]

        # 获取对应的模型名称
        model_name = self.SPACY_MODELS.get(language)
        if not model_name:
            print(f"⚠️  不支持的语言: {language}")
            return None

        # 尝试加载模型
        try:
            import spacy
            try:
                nlp = spacy.load(model_name)
                self.spacy_models[language] = nlp
                print(f"✓ spaCy 模型 ({model_name}) 加载成功")
                return nlp
            except OSError:
                print(f"⚠️  spaCy 模型 {model_name} 未安装")
                print(f"   安装命令: python -m spacy download {model_name}")
                return None
        except ImportError:
            print("⚠️  spaCy 未安装")
            print("   安装命令: pip install spacy")
            return None

    def split_sentences(self, text, language='auto'):
        """
        分句

        参数:
            text: 输入文本
            language: 语言代码 ('auto' 表示自动检测，或指定如 'en', 'zh', 'ja', 'fr' 等)

        返回:
            sentences: 句子列表
        """
        # 自动检测语言
        if language == 'auto':
            if self.auto_detect and self.language_detector:
                language = self.language_detector.detect(text)
                print(f"检测到语言: {language}")
            else:
                # 如果没有语言检测器，默认使用英语
                language = 'en'
                print("⚠️  未启用语言检测，使用默认语言: en")

        # 使用对应的分句器
        if language == 'zh':
            return self._split_chinese(text)
        elif language in self.SPACY_MODELS:
            return self._split_with_spacy(text, language)
        else:
            # 不支持的语言，使用简单规则分句
            print(f"⚠️  语言 {language} 不支持，使用简单规则分句")
            return self._simple_split(text)

    def _split_with_spacy(self, text, language):
        """
        使用 spaCy 分句

        参数:
            text: 输入文本
            language: 语言代码

        返回:
            sentences: 句子列表
        """
        nlp = self._load_spacy_model(language)

        if nlp:
            # 使用 spaCy 分句
            doc = nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents]
        else:
            # 如果模型加载失败，使用简单规则分句
            sentences = self._simple_split(text)

        return [s for s in sentences if s]

    def _split_chinese(self, text):
        """
        中文分句

        参数:
            text: 中文文本

        返回:
            sentences: 句子列表
        """
        if self.hanlp_split_sentence:
            # 使用 HanLP 的规则分句器
            # split_sentence 返回生成器，需要转换为列表
            sentences = list(self.hanlp_split_sentence(text))
        else:
            # 使用简单规则分句
            sentences = self._simple_split_chinese(text)

        return [s for s in sentences if s]

    def _simple_split(self, text):
        """
        简单的通用分句规则（用于不支持的语言）

        参数:
            text: 输入文本

        返回:
            sentences: 句子列表
        """
        # 移除段落间的换行符
        text = text.replace('\n', ' ')
        # 按句号、问号、感叹号分句
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _simple_split_chinese(self, text):
        """
        简单的中文分句规则

        参数:
            text: 中文文本

        返回:
            sentences: 句子列表
        """
        # 移除段落间的换行符
        text = text.replace('\n', '')
        # 按中文句号、问号、感叹号分句
        sentences = re.split(r'[。！？]+', text)
        return [s.strip() for s in sentences if s.strip()]

