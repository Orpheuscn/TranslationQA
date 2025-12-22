#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试对齐问题"""

from translation_qa_tool import TranslationQA

# 从截图看到的文本
source_text = """Sī quis in hōc artem populī nōn nōvit amandī, hoc legat et lēctō carmine doctus amet.
Arte citae vēlōque ratēs rēmōque moventur, arte levēs currūs: arte regendus Amor.
Curribus Automedon lentīsque erat aptus habēnīs, Tīphys in Haemoniā puppe magister erat: mē Venus artificem tenerō praefēcit Amōrī; Tīphys et Automedōn dīcar Amōris ego.
ille quidem ferus est et quī mihi saepe repugnet: sed puer est, aetās mollis et apta regī.
Phīllyrīdēs puerum citharā perfēcit Achillem, atque animos placidā contudit arte ferōs.
quī totiēns sociōs, totiēns exterruit hostēs, crēditur annōsae pertimuisse lyrae."""

target_text = """假如在我们国人中有人不懂得爱术，他只要读了这首诗，读到他便懂爱，他便会爱了。
用船和桨使船儿航行得很快的是艺术，使车儿能行得很轻的是艺术：艺术亦应被用治情爱尔。
奥托墨冬擅于驾车和运用那柔顺的马缰；谛费斯是海蒙尼亚的船的舵工。
而我呢，维纳斯曾经叫我做过她的小阿谟尔的老师；人们将称我为阿道尼斯的谛费斯和奥托墨冬。
他是生来倔强的，他时常向我顽抗，但是他是个孩子，柔顺的年龄，是听人指挥的。
菲丽拉的儿子用琴韵来教育阿喀琉斯，靠这平和的艺术，制服了他的野性。
这个人，他多少次使他的同伴和他的敌人总惊慌。
有人说曾见他在一个衰颓的老人前却战颤着"""

# 创建工具实例（启用自动拆散N:M对齐）
tool = TranslationQA(auto_split_nm=True)

print("="*80)
print("执行对齐...")
print("="*80)

results = tool.check_translation(
    source_text=source_text,
    target_text=target_text,
    source_language='la',
    target_language='zh'
)

print("\n" + "="*80)
print("对齐结果")
print("="*80)

for idx, item in enumerate(results['alignments']):
    print(f"\n对齐组 {idx}:")
    print(f"  源索引: {item['src_indices']}")
    print(f"  目标索引: {item['tgt_indices']}")
    print(f"  相似度: {item['similarity']:.4f}")
    
    src_texts = item.get('src_texts', [item['src_text']])
    tgt_texts = item.get('tgt_texts', [item['tgt_text']])
    
    for i, src in enumerate(src_texts):
        print(f"  源句子{i}: {src[:80]}...")
    for i, tgt in enumerate(tgt_texts):
        print(f"  目标句子{i}: {tgt[:80]}...")

print("\n" + "="*80)
print("源句子列表")
print("="*80)
for i, sent in enumerate(results['source_sentences']):
    print(f"{i}: {sent[:80]}...")

print("\n" + "="*80)
print("目标句子列表")
print("="*80)
for i, sent in enumerate(results['target_sentences']):
    print(f"{i}: {sent[:80]}...")

