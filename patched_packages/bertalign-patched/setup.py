#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bertalign-macos-patched",
    version="0.1.0.post1",
    author="Original: bfsujason, Patched by: Patrick",
    author_email="",
    description="Bertalign with macOS ARM64 patches (ONNX support, FAISS fix, no Google Translate)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bfsujason/bertalign",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
        "faiss-cpu>=1.7.0",
        "onnxruntime>=1.10.0",
        "transformers>=4.0.0",
    ],
)

