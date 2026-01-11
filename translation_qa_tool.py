#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量检查工具 (Translation Quality Assurance Tool)

功能：
1. 使用Bertalign进行N:M句子对齐
2. 使用LaBSE ONNX计算语义相似度
3. 检测三种翻译异常：
   - 缺失 (Omission): 原文句子在译文中没有对应
   - 增添 (Addition): 译文句子在原文中没有对应
   - 相似度低/语义歪曲 (Low Similarity): 对齐组相似度低于阈值
"""

import numpy as np
import json
import pandas as pd
from datetime import datetime
from bertalign import Bertalign
from labse_onnx_encoder import LaBSEOnnxEncoder
from text_splitter import TextSplitter
from model_config import setup_hanlp_env

# 设置 HanLP 环境变量（使用本地模型）
setup_hanlp_env()


class TranslationQA:
    """翻译质量检查工具"""

    def __init__(self, similarity_threshold=0.7, max_align=6, top_k=5, score_threshold=0.15,
                 skip=-1.0, win=10, auto_detect_language=True,
                 force_split_threshold=0.5, use_min_similarity=True, auto_split_nm=False):
        """
        初始化翻译质量检查工具

        参数:
            similarity_threshold: 相似度阈值，低于此值视为语义歪曲
            max_align: Bertalign的最大对齐数 (N:M中的max(N,M))
            top_k: Bertalign的top-k参数
            score_threshold: Bertalign的分数阈值
            skip: Bertalign的跳过惩罚（负数越大，越倾向于N:M对齐而非缺失/增添）
            win: Bertalign的窗口大小
            auto_detect_language: 是否自动检测语言（使用 fastText）
            force_split_threshold: 强制拆散阈值，低于此值的对齐组将被拆散为缺失+增添 (默认0.5)
            use_min_similarity: N:M对齐时使用最小相似度而非平均相似度 (默认True，更严格)
            auto_split_nm: 自动拆散N:M对齐为多个1:1对齐（如果N==M且拆散后相似度更高）(默认False)
        """
        self.similarity_threshold = similarity_threshold
        self.max_align = max_align
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.skip = skip
        self.win = win
        self.force_split_threshold = force_split_threshold
        self.auto_split_nm = auto_split_nm
        self.use_min_similarity = use_min_similarity

        # 初始化编码器（用于计算相似度）
        self.encoder = LaBSEOnnxEncoder()

        # 初始化分句器（支持多语言自动检测）
        self.text_splitter = TextSplitter(auto_detect=auto_detect_language)

        print(f"✓ 翻译质量检查工具初始化完成")
        print(f"  相似度阈值: {similarity_threshold}")
        print(f"  最大对齐数: {max_align}")
        print(f"  分数阈值: {score_threshold}")
        print(f"  跳过惩罚: {skip} (越负越倾向N:M对齐)")
    
    def check_translation(self, source_text, target_text, is_split=True,
                         source_language='auto', target_language='auto'):
        """
        检查翻译质量

        参数:
            source_text: 原文文本（字符串或句子列表）
            target_text: 译文文本（字符串或句子列表）
            is_split: 是否已经分句
            source_language: 源语言 ('en', 'zh', 'auto')
            target_language: 目标语言 ('en', 'zh', 'auto')

        返回:
            results: 检查结果字典
        """
        print("\n" + "="*80)
        print("开始翻译质量检查")
        print("="*80)

        # 步骤0: 文本分句（如果需要）
        detected_src_lang = None
        detected_tgt_lang = None

        if not is_split:
            print("\n步骤0: 文本分句...")
            if isinstance(source_text, str):
                source_sents = self.text_splitter.split_sentences(source_text, source_language)
                # 🆕 获取检测到的语言（用于传递给 Bertalign，避免调用 Google Translate）
                if source_language == 'auto' and self.text_splitter.language_detector:
                    detected_src_lang = self.text_splitter.language_detector.detect(source_text)
                    print(f"  检测到源语言: {detected_src_lang}")
                elif source_language != 'auto':
                    detected_src_lang = source_language
                else:
                    # 如果是 'auto' 但语言检测器不可用，使用默认语言
                    detected_src_lang = 'en'
                    print(f"  ⚠️  语言检测不可用，使用默认源语言: {detected_src_lang}")
                print(f"  源文本分句: {len(source_sents)}句")
            else:
                source_sents = source_text

            if isinstance(target_text, str):
                target_sents = self.text_splitter.split_sentences(target_text, target_language)
                # 🆕 获取检测到的语言（用于传递给 Bertalign，避免调用 Google Translate）
                if target_language == 'auto' and self.text_splitter.language_detector:
                    detected_tgt_lang = self.text_splitter.language_detector.detect(target_text)
                    print(f"  检测到目标语言: {detected_tgt_lang}")
                elif target_language != 'auto':
                    detected_tgt_lang = target_language
                else:
                    # 如果是 'auto' 但语言检测器不可用，使用默认语言
                    detected_tgt_lang = 'zh'
                    print(f"  ⚠️  语言检测不可用，使用默认目标语言: {detected_tgt_lang}")
                print(f"  目标文本分句: {len(target_sents)}句")
            else:
                target_sents = target_text

            # 转换为Bertalign需要的格式（换行分隔）
            source_text_for_align = '\n'.join(source_sents)
            target_text_for_align = '\n'.join(target_sents)
            is_split = True
        else:
            source_text_for_align = source_text
            target_text_for_align = target_text

        # 步骤1: 使用Bertalign进行句子对齐
        print("\n步骤1: 执行句子对齐...")

        aligner = Bertalign(
            src=source_text_for_align,
            tgt=target_text_for_align,
            max_align=self.max_align,
            top_k=self.top_k,
            skip=self.skip,
            win=self.win,
            is_split=is_split,
            src_lang=detected_src_lang,  # 🆕 传入语言代码，避免调用 Google Translate
            tgt_lang=detected_tgt_lang   # 🆕 传入语言代码，避免调用 Google Translate
        )
        aligner.align_sents()
        
        src_sents = aligner.src_sents
        tgt_sents = aligner.tgt_sents
        alignments = aligner.result
        
        print(f"✓ 对齐完成: {len(src_sents)}句源文本 → {len(tgt_sents)}句目标文本")
        print(f"  共{len(alignments)}个对齐组")
        
        # 步骤2: 计算每个对齐组的相似度
        print("\n步骤2: 计算语义相似度...")
        alignment_scores = []

        for src_indices, tgt_indices in alignments:
            # 🔴 修复: 先检查是否为空对齐（缺失/增添）
            if len(src_indices) == 0 or len(tgt_indices) == 0:
                # 空对齐，跳过相似度计算，标记为null
                alignment_scores.append({
                    'src_indices': [int(i) for i in src_indices],
                    'tgt_indices': [int(i) for i in tgt_indices],
                    'src_texts': [src_sents[i] for i in src_indices] if len(src_indices) > 0 else [],
                    'tgt_texts': [tgt_sents[i] for i in tgt_indices] if len(tgt_indices) > 0 else [],
                    'src_text': " ".join([src_sents[i] for i in src_indices]) if len(src_indices) > 0 else "",
                    'tgt_text': " ".join([tgt_sents[i] for i in tgt_indices]) if len(tgt_indices) > 0 else "",
                    'similarity': None,  # 标记为None而非0.0
                    'is_null_alignment': True
                })
                continue

            # 提取句子文本
            src_texts = [src_sents[i] for i in src_indices]
            tgt_texts = [tgt_sents[i] for i in tgt_indices]

            # 🆕 对于N:M对齐，使用最小相似度策略（更严格）
            if self.use_min_similarity and (len(src_texts) > 1 or len(tgt_texts) > 1):
                # 编码所有句子
                src_embeddings = self.encoder.encode_sentences(src_texts)
                tgt_embeddings = self.encoder.encode_sentences(tgt_texts)

                # 计算所有源-目标句子对的相似度，取最小值
                min_sim = 1.0
                for src_emb in src_embeddings:
                    src_emb = src_emb / np.linalg.norm(src_emb)
                    for tgt_emb in tgt_embeddings:
                        tgt_emb = tgt_emb / np.linalg.norm(tgt_emb)
                        sim = float(np.dot(src_emb, tgt_emb))
                        min_sim = min(min_sim, sim)

                similarity = min_sim
            else:
                # 1:1对齐或使用平均相似度策略
                # 编码源句子
                src_embeddings = self.encoder.encode_sentences(src_texts)
                src_emb = np.mean(src_embeddings, axis=0)
                src_emb = src_emb / np.linalg.norm(src_emb)

                # 编码目标句子
                tgt_embeddings = self.encoder.encode_sentences(tgt_texts)
                tgt_emb = np.mean(tgt_embeddings, axis=0)
                tgt_emb = tgt_emb / np.linalg.norm(tgt_emb)

                # 计算余弦相似度
                similarity = float(np.dot(src_emb, tgt_emb))

            alignment_scores.append({
                'src_indices': [int(i) for i in src_indices],
                'tgt_indices': [int(i) for i in tgt_indices],
                'src_texts': src_texts,  # 保留单独的句子列表
                'tgt_texts': tgt_texts,  # 保留单独的句子列表
                'src_text': " ".join(src_texts),  # 合并文本用于显示
                'tgt_text': " ".join(tgt_texts),  # 合并文本用于显示
                'similarity': similarity,
                'is_null_alignment': False
            })

        print(f"✓ 相似度计算完成")

        # 步骤2.5: 自动拆散N:M对齐（如果启用）
        if self.auto_split_nm:
            print("\n步骤2.5: 检查是否需要拆散N:M对齐...")
            new_alignment_scores = []
            split_count = 0

            for item in alignment_scores:
                if item.get('is_null_alignment', False):
                    new_alignment_scores.append(item)
                    continue

                src_indices = item['src_indices']
                tgt_indices = item['tgt_indices']

                # 只处理N:N对齐（N==M且N>1）
                if len(src_indices) == len(tgt_indices) and len(src_indices) > 1:
                    # 计算拆散后的1:1相似度
                    individual_sims = []
                    for i in range(len(src_indices)):
                        src_emb = self.encoder.encode_sentences([item['src_texts'][i]])[0]
                        tgt_emb = self.encoder.encode_sentences([item['tgt_texts'][i]])[0]
                        src_emb = src_emb / np.linalg.norm(src_emb)
                        tgt_emb = tgt_emb / np.linalg.norm(tgt_emb)
                        sim = float(np.dot(src_emb, tgt_emb))
                        individual_sims.append(sim)

                    # 如果所有1:1相似度都高于N:N相似度，则拆散
                    avg_individual_sim = np.mean(individual_sims)
                    if avg_individual_sim > item['similarity']:
                        # 拆散为多个1:1对齐
                        for i in range(len(src_indices)):
                            new_alignment_scores.append({
                                'src_indices': [src_indices[i]],
                                'tgt_indices': [tgt_indices[i]],
                                'src_texts': [item['src_texts'][i]],
                                'tgt_texts': [item['tgt_texts'][i]],
                                'src_text': item['src_texts'][i],
                                'tgt_text': item['tgt_texts'][i],
                                'similarity': individual_sims[i],
                                'is_null_alignment': False
                            })
                        split_count += 1
                    else:
                        new_alignment_scores.append(item)
                else:
                    new_alignment_scores.append(item)

            alignment_scores = new_alignment_scores
            if split_count > 0:
                print(f"✓ 拆散了 {split_count} 个N:M对齐")

        # 步骤3: 检测异常
        print("\n步骤3: 检测翻译异常...")

        # 🔴 修复: 先从空对齐中提取缺失/增添
        omissions = []
        additions = []
        low_similarity = []

        # 🆕 强制拆散的对齐组（用于后续补充缺失/增添）
        force_split_alignments = []

        for item in alignment_scores:
            if item.get('is_null_alignment', False):
                # 空对齐：判断是缺失还是增添
                if len(item['src_indices']) > 0 and len(item['tgt_indices']) == 0:
                    # 缺失：有源无目标
                    for idx in item['src_indices']:
                        omissions.append({
                            'type': 'omission',
                            'src_index': idx,
                            'src_text': src_sents[idx]
                        })
                elif len(item['src_indices']) == 0 and len(item['tgt_indices']) > 0:
                    # 增添：无源有目标
                    for idx in item['tgt_indices']:
                        additions.append({
                            'type': 'addition',
                            'tgt_index': idx,
                            'tgt_text': tgt_sents[idx]
                        })
            else:
                # 🆕 事后清洗：强制拆散低相似度对齐组
                if item['similarity'] < self.force_split_threshold:
                    # 相似度极低，强制拆散为缺失+增添
                    for idx in item['src_indices']:
                        omissions.append({
                            'type': 'omission',
                            'src_index': idx,
                            'src_text': src_sents[idx]
                        })
                    for idx in item['tgt_indices']:
                        additions.append({
                            'type': 'addition',
                            'tgt_index': idx,
                            'tgt_text': tgt_sents[idx]
                        })
                    # 记录被拆散的对齐组
                    force_split_alignments.append(item)
                # 有效对齐：检查相似度
                elif item['similarity'] < self.similarity_threshold:
                    low_similarity.append({
                        'type': 'low_similarity',
                        'src_indices': item['src_indices'],
                        'tgt_indices': item['tgt_indices'],
                        'src_text': item['src_text'],
                        'tgt_text': item['tgt_text'],
                        'similarity': item['similarity']
                    })

        # 3.1 检测未被任何对齐覆盖的句子（补充检查）
        # 🆕 排除被强制拆散的对齐组
        aligned_src_indices = set()
        aligned_tgt_indices = set()

        # 收集已经添加到缺失/增添的索引（来自强制拆散）
        existing_omission_indices = set(item['src_index'] for item in omissions)
        existing_addition_indices = set(item['tgt_index'] for item in additions)

        for item in alignment_scores:
            if item in force_split_alignments:
                # 被拆散的对齐组，已经在前面处理为缺失+增添，不需要再处理
                pass
            else:
                aligned_src_indices.update(item['src_indices'])
                aligned_tgt_indices.update(item['tgt_indices'])

        # 补充缺失（排除已经添加过的）
        for i in range(len(src_sents)):
            if i not in aligned_src_indices and i not in existing_omission_indices:
                omissions.append({
                    'type': 'omission',
                    'src_index': i,
                    'src_text': src_sents[i]
                })

        # 补充增添（排除已经添加过的）
        for i in range(len(tgt_sents)):
            if i not in aligned_tgt_indices and i not in existing_addition_indices:
                additions.append({
                    'type': 'addition',
                    'tgt_index': i,
                    'tgt_text': tgt_sents[i]
                })
        
        print(f"✓ 异常检测完成:")
        print(f"  缺失 (Omission): {len(omissions)}处")
        print(f"  增添 (Addition): {len(additions)}处")
        print(f"  相似度低 (Low Similarity): {len(low_similarity)}处")
        if force_split_alignments:
            print(f"  强制拆散对齐组: {len(force_split_alignments)}个 (相似度 < {self.force_split_threshold})")
        
        # 汇总结果
        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'source_sentences': len(src_sents),
                'target_sentences': len(tgt_sents),
                'alignments': len(alignments),
                'similarity_threshold': self.similarity_threshold,
                'force_split_threshold': self.force_split_threshold
            },
            'alignments': alignment_scores,
            'force_split_alignments': force_split_alignments,  # 🆕 记录被拆散的对齐组
            'issues': {
                'omissions': omissions,
                'additions': additions,
                'low_similarity': low_similarity
            },
            'summary': {
                'total_issues': len(omissions) + len(additions) + len(low_similarity),
                'omission_count': len(omissions),
                'addition_count': len(additions),
                'low_similarity_count': len(low_similarity),
                'force_split_count': len(force_split_alignments)  # 🆕
            }
        }

        return results

    def save_report_json(self, results, output_path="translation_qa_report.json"):
        """
        保存JSON格式报告

        参数:
            results: check_translation()返回的结果
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n✓ JSON报告已保存: {output_path}")

    def save_report_csv(self, results, output_path="translation_qa_report.csv"):
        """
        保存CSV格式报告（按要求的多行平铺格式）

        格式说明：
        - 1:N对齐：源文本只在第一行显示，后续行留空；目标文本每行显示一句
        - N:1对齐：目标文本只在第一行显示，后续行留空；源文本每行显示一句
        - N:M对齐：按max(N,M)展开，超出部分留空

        参数:
            results: check_translation()返回的结果
            output_path: 输出文件路径
        """
        # 🔴 修复: 将所有行合并到一个列表，然后按源索引排序
        all_rows = []

        # 🆕 获取被拆散的对齐组列表
        force_split_set = set()
        for fs_item in results.get('force_split_alignments', []):
            # 使用对齐组的索引标识（通过src_indices和tgt_indices的元组）
            force_split_set.add((tuple(fs_item['src_indices']), tuple(fs_item['tgt_indices'])))

        # 对齐组 - 按要求的格式平铺
        for alignment_idx, item in enumerate(results['alignments']):
            src_indices = item['src_indices']
            tgt_indices = item['tgt_indices']
            src_texts = item.get('src_texts', [item['src_text']])
            tgt_texts = item.get('tgt_texts', [item['tgt_text']])
            similarity = item['similarity']

            # 🆕 跳过被拆散的对齐组
            if (tuple(src_indices), tuple(tgt_indices)) in force_split_set:
                continue

            # 判断异常类型
            if similarity is None:
                # 空对齐，已在Step 3中处理为缺失/增添
                continue
            elif similarity < self.similarity_threshold:
                exception_type = '相似度低 (Low Similarity)'
            else:
                exception_type = 'OK'

            # 计算需要的行数
            max_rows = max(len(src_indices), len(tgt_indices))

            # 🔴 修复: 使用第一个源索引作为排序键（如果有源索引的话）
            # 对于N:M对齐，所有行都应该使用相同的排序键，这样它们会被排在一起
            if len(src_indices) > 0:
                sort_key = src_indices[0]
            elif len(tgt_indices) > 0:
                # 如果没有源索引（增添），使用目标索引 + 大偏移量
                sort_key = 999999 + tgt_indices[0]
            else:
                sort_key = 999999

            # 按要求的逻辑平铺
            for row_idx in range(max_rows):
                # 确定当前行显示的源文本和目标文本
                if row_idx < len(src_texts):
                    src_text = src_texts[row_idx]
                    src_idx = src_indices[row_idx]
                else:
                    src_text = ''
                    src_idx = ''

                if row_idx < len(tgt_texts):
                    tgt_text = tgt_texts[row_idx]
                    tgt_idx = tgt_indices[row_idx]
                else:
                    tgt_text = ''
                    tgt_idx = ''

                # 第一行显示相似度和异常情况
                if row_idx == 0:
                    show_similarity = f"{similarity:.4f}"
                    show_exception = exception_type
                else:
                    show_similarity = ''
                    show_exception = exception_type if exception_type != 'OK' else ''

                # 🔴 修复: 为了保持N:M对齐的多行在一起，使用子排序键
                # sort_key相同时，按row_idx排序
                subsort_key = sort_key + (row_idx * 0.001)  # 添加小数部分来保持顺序

                all_rows.append({
                    '原文 (Source)': src_text,
                    '译文 (Target)': tgt_text,
                    '源索引': src_idx,
                    '目标索引': tgt_idx,
                    '相似度 (Similarity)': show_similarity,
                    '异常情况 (Exception)': show_exception,
                    '_sort_key': subsort_key  # 使用子排序键
                })

        # 缺失 (Omission)
        for item in results['issues']['omissions']:
            all_rows.append({
                '原文 (Source)': item['src_text'],
                '译文 (Target)': '',
                '源索引': item['src_index'],
                '目标索引': '',
                '相似度 (Similarity)': '',
                '异常情况 (Exception)': '缺失 (Omission)',
                '_sort_key': item['src_index']
            })

        # 增添 (Addition)
        for item in results['issues']['additions']:
            all_rows.append({
                '原文 (Source)': '',
                '译文 (Target)': item['tgt_text'],
                '源索引': '',
                '目标索引': item['tgt_index'],
                '相似度 (Similarity)': '',
                '异常情况 (Exception)': '增添 (Addition)',
                '_sort_key': 999999 + item['tgt_index']  # 增添排在最后
            })

        # 🔴 修复: 按源索引排序
        all_rows.sort(key=lambda x: x['_sort_key'])

        # 移除排序键
        for row in all_rows:
            del row['_sort_key']

        df = pd.DataFrame(all_rows)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"✓ CSV报告已保存: {output_path}")

    def print_summary(self, results):
        """
        打印检查结果摘要

        参数:
            results: check_translation()返回的结果
        """
        print("\n" + "="*80)
        print("翻译质量检查报告")
        print("="*80)

        print(f"\n📊 统计信息:")
        print(f"  源文本句子数: {results['metadata']['source_sentences']}")
        print(f"  目标文本句子数: {results['metadata']['target_sentences']}")
        print(f"  对齐组数: {results['metadata']['alignments']}")
        print(f"  相似度阈值: {results['metadata']['similarity_threshold']}")

        print(f"\n⚠️  发现的问题:")
        print(f"  总计: {results['summary']['total_issues']}处")
        print(f"  - 缺失 (Omission): {results['summary']['omission_count']}处")
        print(f"  - 增添 (Addition): {results['summary']['addition_count']}处")
        print(f"  - 相似度低 (Low Similarity): {results['summary']['low_similarity_count']}处")

        # 详细列出问题
        if results['issues']['omissions']:
            print(f"\n❌ 缺失 (Omission):")
            for item in results['issues']['omissions']:
                print(f"  源句子[{item['src_index']}]: {item['src_text'][:60]}...")

        if results['issues']['additions']:
            print(f"\n➕ 增添 (Addition):")
            for item in results['issues']['additions']:
                print(f"  目标句子[{item['tgt_index']}]: {item['tgt_text'][:60]}...")

        if results['issues']['low_similarity']:
            print(f"\n⚠️  相似度低 (Low Similarity < {self.similarity_threshold}):")
            for item in results['issues']['low_similarity']:
                print(f"  相似度: {item['similarity']:.4f}")
                print(f"    源: {item['src_text'][:60]}...")
                print(f"    译: {item['tgt_text'][:60]}...")

        print("\n" + "="*80)

