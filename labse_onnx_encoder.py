#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaBSE ONNX Encoder - 替代Bertalign的默认encoder
"""

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer


def yield_overlaps(sents, num_overlaps):
    """
    生成重叠窗口 (从bertalign.utils复制，避免导入bertalign包)

    参数:
        sents: 句子列表
        num_overlaps: 重叠窗口数量

    生成:
        重叠的句子组合
    """
    for i in range(len(sents)):
        for j in range(num_overlaps):
            if i + j < len(sents):
                yield " ".join(sents[i:i+j+1])
            else:
                yield sents[-1]


class LaBSEOnnxEncoder:
    """
    使用ONNX格式的LaBSE模型进行句子编码
    兼容Bertalign的Encoder接口
    """
    
    def __init__(self, model_path=None):
        """
        初始化LaBSE ONNX编码器

        参数:
            model_path: ONNX模型目录路径（默认为脚本所在目录下的labse_onnx）
        """
        import os

        # 如果未指定路径，使用脚本所在目录下的labse_onnx
        if model_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, "labse_onnx")

        self.model_name = "LaBSE-ONNX"
        self.model_path = model_path

        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        # 加载ONNX模型
        onnx_model_path = os.path.join(model_path, "model.onnx")
        self.session = ort.InferenceSession(onnx_model_path)

        print(f"✓ LaBSE ONNX编码器初始化成功 (模型路径: {model_path})")
    
    def encode_sentences(self, sentences):
        """
        编码句子列表为嵌入向量
        
        参数:
            sentences: 句子列表
        
        返回:
            embeddings: (n_sentences, hidden_size) 归一化的嵌入向量
        """
        # Tokenize
        inputs = self.tokenizer(
            sentences, 
            padding=True, 
            truncation=True, 
            max_length=512,
            return_tensors="np"
        )
        
        # 准备ONNX输入
        onnx_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
            "token_type_ids": inputs["token_type_ids"].astype(np.int64),
        }
        
        # 运行推理
        outputs = self.session.run(None, onnx_inputs)
        
        # 提取[CLS] token的嵌入
        embeddings = outputs[0][:, 0, :].astype(np.float32)
        
        # L2归一化
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        return embeddings
    
    def transform(self, sents, num_overlaps):
        """
        Bertalign兼容的transform方法
        
        参数:
            sents: 句子列表
            num_overlaps: 重叠窗口数量 (用于N:M对齐)
        
        返回:
            sent_vecs: (num_overlaps, n_sents, hidden_size) 句子向量
            len_vecs: (num_overlaps, n_sents) 句子长度
        """
        # 生成重叠窗口
        overlaps = []
        for line in yield_overlaps(sents, num_overlaps):
            overlaps.append(line)
        
        # 编码所有重叠窗口
        sent_vecs = self.encode_sentences(overlaps)
        
        # Reshape为 (num_overlaps, n_sents, hidden_size)
        embedding_dim = sent_vecs.shape[1]
        sent_vecs = sent_vecs.reshape(num_overlaps, len(sents), embedding_dim)
        
        # 计算句子长度 (字节数)
        len_vecs = np.array([len(line.encode("utf-8")) for line in overlaps])
        len_vecs = len_vecs.reshape(num_overlaps, len(sents))
        
        return sent_vecs, len_vecs


# 测试编码器
if __name__ == "__main__":
    print("=" * 80)
    print("测试 LaBSE ONNX Encoder")
    print("=" * 80)
    
    # 初始化编码器
    encoder = LaBSEOnnxEncoder()
    
    # 测试句子
    test_sents = [
        "The Quantum Processor (QP) is the core unit of the system.",
        "It handles all critical computations.",
        "量子处理器(QP)是系统的核心。",
    ]
    
    print(f"\n测试transform方法 (num_overlaps=3)...")
    sent_vecs, len_vecs = encoder.transform(test_sents, num_overlaps=3)
    
    print(f"✓ Transform成功!")
    print(f"  sent_vecs形状: {sent_vecs.shape}")
    print(f"  len_vecs形状: {len_vecs.shape}")
    print(f"  sent_vecs dtype: {sent_vecs.dtype}")
    
    print("\n" + "="*80)
    print("✓ LaBSE ONNX Encoder测试成功!")
    print("="*80)

