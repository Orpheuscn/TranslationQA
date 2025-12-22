#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量检查工具 - Web服务器
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
from translation_qa_tool import TranslationQA
from word_aligner import WordAligner

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局QA工具实例（复用以提高性能）
qa_tool = None
word_aligner = None


def get_qa_tool():
    """获取或初始化QA工具实例"""
    global qa_tool
    if qa_tool is None:
        print("初始化翻译质量检查工具...")
        qa_tool = TranslationQA(
            similarity_threshold=0.7,
            max_align=6,
            top_k=5,
            skip=-1.0,
            win=10,
            auto_detect_language=True,  # 启用自动语言检测（使用fastText）
            force_split_threshold=0.3,  # 降低阈值（0.5 -> 0.3），避免误拆散
            use_min_similarity=False    # 使用平均相似度（更宽松）
        )
        print("✓ 工具初始化完成")
    return qa_tool


def get_word_aligner():
    """获取或初始化词对齐器实例"""
    global word_aligner
    if word_aligner is None:
        print("初始化词对齐器...")
        word_aligner = WordAligner()
        print("✓ 词对齐器初始化完成")
    return word_aligner


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def check_translation():
    """
    翻译质量检查API

    请求体:
    {
        "source_text": "原文",
        "target_text": "译文",
        "similarity_threshold": 0.7,      // 可选，相似度阈值
        "force_split_threshold": 0.5,     // 可选，强制拆散阈值
        "max_align": 5,                   // 可选，最大对齐数
        "top_k": 3,                       // 可选，Top-K参数
        "skip": -0.1,                     // 可选，跳过惩罚
        "win": 5,                         // 可选，窗口大小
        "score_threshold": 0.0,           // 可选，分数阈值
        "use_min_similarity": true        // 可选，使用最小相似度
    }

    返回:
    {
        "success": true,
        "data": {
            "csv": "CSV格式的报告",
            "summary": {...},
            "issues": {...}
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        source_text = data.get('source_text', '').strip()
        target_text = data.get('target_text', '').strip()
        
        if not source_text or not target_text:
            return jsonify({
                'success': False,
                'error': '原文和译文不能为空'
            }), 400
        
        # 获取可选参数
        similarity_threshold = data.get('similarity_threshold', 0.7)
        force_split_threshold = data.get('force_split_threshold', 0.5)

        # 获取高级参数
        max_align = data.get('max_align', 5)
        top_k = data.get('top_k', 3)
        skip = data.get('skip', -0.1)
        win = data.get('win', 5)
        score_threshold = data.get('score_threshold', 0.0)
        use_min_similarity = data.get('use_min_similarity', True)
        auto_split_nm = data.get('auto_split_nm', True)  # 默认启用自动拆散

        # 更新参数（如果与当前不同）
        tool = get_qa_tool()
        tool.similarity_threshold = similarity_threshold
        tool.force_split_threshold = force_split_threshold
        tool.max_align = max_align
        tool.top_k = top_k
        tool.skip = skip
        tool.win = win
        tool.score_threshold = score_threshold
        tool.use_min_similarity = use_min_similarity
        tool.auto_split_nm = auto_split_nm

        # 执行检查（使用 fastText 自动检测语言）
        print(f"开始检查翻译...")
        print(f"  使用 fastText 自动检测语言...")

        results = tool.check_translation(
            source_text=source_text,
            target_text=target_text,
            source_language='auto',  # 自动检测
            target_language='auto',  # 自动检测
            is_split=False  # 让工具自动分句
        )
        
        # 生成CSV格式的报告
        csv_lines = []
        csv_lines.append("原文 (Source),译文 (Target),源索引,目标索引,相似度 (Similarity),异常情况 (Exception)")
        
        # 收集所有行
        all_rows = []
        
        # 获取被拆散的对齐组
        force_split_set = set()
        for fs_item in results.get('force_split_alignments', []):
            force_split_set.add((tuple(fs_item['src_indices']), tuple(fs_item['tgt_indices'])))
        
        # 对齐组
        for item in results['alignments']:
            src_indices = item['src_indices']
            tgt_indices = item['tgt_indices']

            # 跳过被拆散的对齐组
            if (tuple(src_indices), tuple(tgt_indices)) in force_split_set:
                continue

            similarity = item['similarity']

            # 检查异常
            exception = "OK"
            if similarity is None:
                exception = "空对齐"
            elif similarity < similarity_threshold:
                exception = "相似度低 (Low Similarity)"

            # 🔴 修复: 使用第一个源索引作为排序键（如果有源索引的话）
            # 对于N:M对齐，所有行都应该使用相同的排序键，这样它们会被排在一起
            if len(src_indices) > 0:
                sort_key = src_indices[0]
            elif len(tgt_indices) > 0:
                # 如果没有源索引（增添），使用目标索引 + 大偏移量
                sort_key = 999999 + tgt_indices[0]
            else:
                sort_key = 999999

            # N:M对齐展开
            max_len = max(len(src_indices), len(tgt_indices))
            for i in range(max_len):
                src_text = item['src_texts'][i] if i < len(item['src_texts']) else ""
                tgt_text = item['tgt_texts'][i] if i < len(item['tgt_texts']) else ""
                src_idx = src_indices[i] if i < len(src_indices) else ""
                tgt_idx = tgt_indices[i] if i < len(tgt_indices) else ""

                # 只有第一行显示相似度和异常情况
                if i == 0:
                    sim_str = f"{similarity:.4f}" if similarity is not None else ""
                    exc_str = exception
                else:
                    sim_str = ""
                    exc_str = exception if exception != "OK" else ""

                # 🔴 修复: 为了保持N:M对齐的多行在一起，使用子排序键
                # sort_key相同时，按i排序
                subsort_key = sort_key + (i * 0.001)  # 添加小数部分来保持顺序

                all_rows.append({
                    'src_text': src_text,
                    'tgt_text': tgt_text,
                    'src_index': src_idx,
                    'tgt_index': tgt_idx,
                    'similarity': sim_str,
                    'exception': exc_str,
                    '_sort_key': subsort_key  # 使用子排序键
                })
        
        # 缺失和增添
        for item in results['issues']['omissions']:
            all_rows.append({
                'src_text': item['src_text'],
                'tgt_text': "",
                'src_index': item['src_index'],
                'tgt_index': "",
                'similarity': "",
                'exception': "缺失 (Omission)",
                '_sort_key': item['src_index']
            })
        
        for item in results['issues']['additions']:
            all_rows.append({
                'src_text': "",
                'tgt_text': item['tgt_text'],
                'src_index': "",
                'tgt_index': item['tgt_index'],
                'similarity': "",
                'exception': "增添 (Addition)",
                '_sort_key': 999999
            })

        # 按源索引排序
        all_rows.sort(key=lambda x: x['_sort_key'])

        # 生成CSV
        for row in all_rows:
            csv_lines.append(f'"{row["src_text"]}","{row["tgt_text"]}",{row["src_index"]},{row["tgt_index"]},{row["similarity"]},{row["exception"]}')

        csv_content = "\n".join(csv_lines)

        # 返回结果
        return jsonify({
            'success': True,
            'data': {
                'csv': csv_content,
                'summary': {
                    # 前端需要的字段
                    'src_count': results['metadata']['source_sentences'],
                    'tgt_count': results['metadata']['target_sentences'],
                    'alignment_count': results['metadata']['alignments'],
                    'similarity_threshold': results['metadata']['similarity_threshold'],
                    # 原有的统计字段
                    'total_issues': results['summary']['total_issues'],
                    'omission_count': results['summary']['omission_count'],
                    'addition_count': results['summary']['addition_count'],
                    'low_similarity_count': results['summary']['low_similarity_count'],
                    'force_split_count': results['summary']['force_split_count']
                },
                'issues': {
                    'omissions': results['issues']['omissions'],
                    'additions': results['issues']['additions'],
                    'low_similarity': results['issues']['low_similarity']
                },
                'force_split_count': len(results.get('force_split_alignments', []))
            }
        })

    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"错误: {error_msg}")
        print(traceback_msg)

        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': traceback_msg
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'model_loaded': qa_tool is not None
    })


@app.route('/api/word-align', methods=['POST'])
def word_align():
    """
    词对齐API

    请求体:
    {
        "source_text": "源句子",
        "target_text": "目标句子",
        "source_lang": "en",  // 可选
        "target_lang": "zh"   // 可选
    }

    返回:
    {
        "success": true,
        "data": {
            "csv": "CSV格式的词对齐结果",
            "alignments": [...]
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400

        source_text = data.get('source_text', '').strip()
        target_text = data.get('target_text', '').strip()

        if not source_text or not target_text:
            return jsonify({
                'success': False,
                'error': '源文本和目标文本不能为空'
            }), 400

        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'auto')

        # 获取词对齐器
        aligner = get_word_aligner()

        # 执行词对齐
        print(f"\n执行词对齐...")
        print(f"  源文本: {source_text}")
        print(f"  目标文本: {target_text}")
        print(f"  源语言: {source_lang}")
        print(f"  目标语言: {target_lang}")

        alignments = aligner.align_words(source_text, target_text, source_lang, target_lang)
        csv_lines = aligner.align_words_to_csv(source_text, target_text, source_lang, target_lang)

        print(f"✓ 词对齐完成: {len(alignments)} 个词对")
        if alignments:
            print(f"  前3个对齐: {alignments[:3]}")

        return jsonify({
            'success': True,
            'data': {
                'csv': '\n'.join(csv_lines),
                'alignments': alignments
            }
        })

    except Exception as e:
        print(f"词对齐错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("="*80)
    print("翻译质量检查工具 - Web服务器")
    print("="*80)
    print("\n正在启动服务器...")
    print("访问地址: http://localhost:5001")
    print("\n按 Ctrl+C 停止服务器\n")

    app.run(host='0.0.0.0', port=5001, debug=True)

