#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查单独的1:1相似度"""

from labse_onnx_encoder import LaBSEOnnxEncoder
import numpy as np

# 初始化编码器
encoder = LaBSEOnnxEncoder()

# 第一对句子
src1 = "Sī quis in hōc artem populī nōn nōvit amandī, hoc legat et lēctō carmine doctus amet."
tgt1 = "假如在我们国人中有人不懂得爱术，他只要读了这首诗，读到他便懂爱，他便会爱了。"

# 第二对句子
src2 = "Arte citae vēlōque ratēs rēmōque moventur, arte levēs currūs: arte regendus Amor."
tgt2 = "用船和桨使船儿航行得很快的是艺术，使车儿能行得很轻的是艺术：艺术亦应被用治情爱尔。"

# 计算单独的相似度
print("="*80)
print("单独的1:1相似度")
print("="*80)

# 第一对
emb_src1 = encoder.encode_sentences([src1])[0]
emb_tgt1 = encoder.encode_sentences([tgt1])[0]
sim1 = np.dot(emb_src1, emb_tgt1) / (np.linalg.norm(emb_src1) * np.linalg.norm(emb_tgt1))
print(f"\n第一对句子:")
print(f"  源: {src1[:60]}...")
print(f"  目标: {tgt1[:60]}...")
print(f"  相似度: {sim1:.4f}")

# 第二对
emb_src2 = encoder.encode_sentences([src2])[0]
emb_tgt2 = encoder.encode_sentences([tgt2])[0]
sim2 = np.dot(emb_src2, emb_tgt2) / (np.linalg.norm(emb_src2) * np.linalg.norm(emb_tgt2))
print(f"\n第二对句子:")
print(f"  源: {src2[:60]}...")
print(f"  目标: {tgt2[:60]}...")
print(f"  相似度: {sim2:.4f}")

# 合并后的相似度
merged_src = src1 + " " + src2
merged_tgt = tgt1 + " " + tgt2
emb_merged_src = encoder.encode_sentences([merged_src])[0]
emb_merged_tgt = encoder.encode_sentences([merged_tgt])[0]
sim_merged = np.dot(emb_merged_src, emb_merged_tgt) / (np.linalg.norm(emb_merged_src) * np.linalg.norm(emb_merged_tgt))
print(f"\n合并后的2:2对齐:")
print(f"  相似度: {sim_merged:.4f}")

print(f"\n结论:")
if sim1 > sim_merged and sim2 > sim_merged:
    print(f"  ✓ 两个1:1对齐的相似度都高于2:2合并，应该拆散")
    print(f"    1:1平均相似度: {(sim1 + sim2) / 2:.4f}")
    print(f"    2:2合并相似度: {sim_merged:.4f}")
else:
    print(f"  ✗ 2:2合并的相似度更高，不应该拆散")

