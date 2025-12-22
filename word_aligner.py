#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词对齐模块

使用 LaBSE 进行词级别的语义对齐
"""

import numpy as np
import re
from labse_onnx_encoder import LaBSEOnnxEncoder


class WordAligner:
    """词对齐器"""

    # 语言代码到 spaCy 模型的映射（与 text_splitter.py 保持一致）
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

    def __init__(self):
        """初始化词对齐器"""
        self.encoder = LaBSEOnnxEncoder()
        self.spacy_models = {}  # 缓存已加载的 spaCy 模型
        self.hanlp_tokenizer = None  # HanLP 分词器

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
            return None

        # 尝试加载模型
        try:
            import spacy
            try:
                nlp = spacy.load(model_name)
                self.spacy_models[language] = nlp
                print(f"✓ 词对齐：spaCy 模型 ({model_name}) 加载成功")
                return nlp
            except OSError:
                print(f"⚠️  词对齐：spaCy 模型 {model_name} 未安装，使用简单规则分词")
                return None
        except ImportError:
            print("⚠️  词对齐：spaCy 未安装，使用简单规则分词")
            return None

    def _load_hanlp_tokenizer(self):
        """
        加载 HanLP 分词器（用于中文）

        返回:
            HanLP 分词器，如果加载失败则返回 None
        """
        if self.hanlp_tokenizer is not None:
            return self.hanlp_tokenizer

        try:
            import hanlp
            # 使用 HanLP 的粗粒度分词器
            self.hanlp_tokenizer = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
            print("✓ 词对齐：HanLP 分词器加载成功")
            return self.hanlp_tokenizer
        except Exception as e:
            print(f"⚠️  词对齐：HanLP 分词器加载失败，使用简单规则分词: {e}")
            return None

    def tokenize(self, text, language='auto'):
        """
        分词

        参数:
            text: 输入文本
            language: 语言代码

        返回:
            words: 词列表
        """
        # 检测是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))

        if has_chinese or language == 'zh':
            # 中文：尝试使用 HanLP 分词
            tokenizer = self._load_hanlp_tokenizer()
            if tokenizer:
                try:
                    words = tokenizer(text)
                    return words
                except:
                    pass

            # 如果 HanLP 不可用，按字符分词
            words = list(text.strip())
            # 过滤空格
            words = [w for w in words if w.strip()]
            return words

        elif language in self.SPACY_MODELS:
            # 使用 spaCy 分词
            nlp = self._load_spacy_model(language)
            if nlp:
                try:
                    doc = nlp(text)
                    words = [token.text for token in doc]
                    return words
                except:
                    pass

        # 默认：简单规则分词（按空格和标点）
        words = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
        return words
    
    def align_words(self, source_text, target_text, source_lang='auto', target_lang='auto'):
        """
        对齐两个句子中的词

        参数:
            source_text: 源文本
            target_text: 目标文本
            source_lang: 源语言
            target_lang: 目标语言

        返回:
            alignments: 对齐结果列表，每个元素为 {
                'source_word': 源词,
                'target_word': 目标词,
                'source_index': 源词索引,
                'target_index': 目标词索引,
                'similarity': 相似度
            }
        """
        # 分词
        print(f"\n[词对齐] 开始分词...")
        print(f"  源文本: {source_text[:100]}...")
        print(f"  目标文本: {target_text[:100]}...")

        source_words = self.tokenize(source_text, source_lang)
        target_words = self.tokenize(target_text, target_lang)

        print(f"  源词数量: {len(source_words)}")
        print(f"  目标词数量: {len(target_words)}")
        print(f"  前10个源词: {source_words[:10]}")
        print(f"  前10个目标词: {target_words[:10]}")
        
        if not source_words or not target_words:
            return []
        
        # 编码所有词
        source_embeddings = self.encoder.encode_sentences(source_words)
        target_embeddings = self.encoder.encode_sentences(target_words)
        
        # 计算相似度矩阵
        similarity_matrix = np.dot(source_embeddings, target_embeddings.T)
        
        # 使用贪心算法进行对齐
        alignments = []
        used_target_indices = set()
        
        for src_idx, src_word in enumerate(source_words):
            # 找到与当前源词最相似的目标词
            similarities = similarity_matrix[src_idx]
            
            # 排除已使用的目标词
            available_similarities = similarities.copy()
            for used_idx in used_target_indices:
                available_similarities[used_idx] = -1
            
            # 找到最大相似度
            tgt_idx = np.argmax(available_similarities)
            max_similarity = available_similarities[tgt_idx]
            
            if max_similarity > 0:  # 只保留正相似度的对齐
                alignments.append({
                    'source_word': src_word,
                    'target_word': target_words[tgt_idx],
                    'source_index': int(src_idx),  # 转换为 Python int
                    'target_index': int(tgt_idx),  # 转换为 Python int
                    'similarity': float(max_similarity)
                })
                used_target_indices.add(tgt_idx)

        # 添加未对齐的目标词
        for tgt_idx, tgt_word in enumerate(target_words):
            if tgt_idx not in used_target_indices:
                alignments.append({
                    'source_word': '-',
                    'target_word': tgt_word,
                    'source_index': -1,
                    'target_index': int(tgt_idx),  # 转换为 Python int
                    'similarity': 0.0
                })
        
        # 按源索引和目标索引排序
        alignments.sort(key=lambda x: (x['source_index'], x['target_index']))
        
        return alignments
    
    def align_words_to_csv(self, source_text, target_text, source_lang='auto', target_lang='auto'):
        """
        将词对齐结果转换为 CSV 格式
        
        参数:
            source_text: 源文本
            target_text: 目标文本
            source_lang: 源语言
            target_lang: 目标语言
        
        返回:
            csv_lines: CSV 行列表
        """
        alignments = self.align_words(source_text, target_text, source_lang, target_lang)
        
        csv_lines = []
        csv_lines.append("源词 (Source Word),目标词 (Target Word),源索引,目标索引,相似度 (Similarity)")
        
        for alignment in alignments:
            csv_lines.append(
                f'"{alignment["source_word"]}","{alignment["target_word"]}",'
                f'{alignment["source_index"]},{alignment["target_index"]},'
                f'{alignment["similarity"]:.4f}'
            )
        
        return csv_lines

