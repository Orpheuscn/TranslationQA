"""
Bertalign-Offline - 修改版 Bertalign（支持离线运行）

基于 Bertalign 0.1.0，添加以下修改：
1. 支持传入语言代码，避免调用 Google Translate API
2. 使用 ONNX 版本的 LaBSE 模型（避免 macOS ARM64 崩溃）
3. 修复 FAISS 在 macOS ARM64 上的批量搜索 bug

原始项目: https://github.com/bfsujason/bertalign
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bertalign-offline",
    version="0.1.0.post1",  # post1 表示这是基于 0.1.0 的修改版
    author="Jason (原作者), Patrick (修改者)",
    author_email="bfsujason@163.com",
    description="修改版 Bertalign - 支持离线运行，无需 Google Translate API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bfsujason/bertalign",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "sentence-splitter>=1.4",
        "googletrans==3.1.0a0",  # 保留依赖，但可选使用
        "faiss-cpu>=1.7.0",
        "numba>=0.56.0",
        "torch>=2.0.0",
        "onnxruntime>=1.15.0",  # 新增：ONNX 支持
        "transformers>=4.30.0",  # 新增：Tokenizer 支持
    ],
    extras_require={
        "gpu": ["faiss-gpu>=1.7.0"],
    },
)

