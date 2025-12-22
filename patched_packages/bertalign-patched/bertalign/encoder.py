import numpy as np
import os

# 修补: 使用ONNX版本避免macOS ARM64上的SentenceTransformer崩溃
USE_ONNX = True

if USE_ONNX:
    import onnxruntime as ort
    from transformers import AutoTokenizer
else:
    from sentence_transformers import SentenceTransformer

from bertalign.utils import yield_overlaps

class Encoder:
    def __init__(self, model_name):
        self.model_name = model_name

        if USE_ONNX:
            # 使用ONNX版本的LaBSE
            model_path = os.path.join(os.getcwd(), "labse_onnx")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"ONNX模型目录不存在: {model_path}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            onnx_model_path = os.path.join(model_path, "model.onnx")
            self.session = ort.InferenceSession(onnx_model_path)
            self.model = None
            print(f"✓ 使用ONNX版本的LaBSE (避免macOS ARM64崩溃)")
        else:
            self.model = SentenceTransformer(model_name)
            self.tokenizer = None
            self.session = None

    def encode_onnx(self, sentences):
        """使用ONNX模型编码句子"""
        inputs = self.tokenizer(
            sentences,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="np"
        )

        onnx_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
            "token_type_ids": inputs["token_type_ids"].astype(np.int64),
        }

        outputs = self.session.run(None, onnx_inputs)
        embeddings = outputs[0][:, 0, :].astype(np.float32)

        # L2归一化
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms

        return embeddings

    def transform(self, sents, num_overlaps):
        overlaps = []
        for line in yield_overlaps(sents, num_overlaps):
            overlaps.append(line)

        if USE_ONNX:
            sent_vecs = self.encode_onnx(overlaps)
        else:
            sent_vecs = self.model.encode(overlaps)

        embedding_dim = sent_vecs.size // (len(sents) * num_overlaps)
        sent_vecs = sent_vecs.reshape(num_overlaps, len(sents), embedding_dim)

        len_vecs = [len(line.encode("utf-8")) for line in overlaps]
        len_vecs = np.array(len_vecs)
        len_vecs = len_vecs.reshape(num_overlaps, len(sents))

        return sent_vecs, len_vecs
