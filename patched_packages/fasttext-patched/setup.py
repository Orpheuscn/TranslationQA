#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fasttext-numpy2-patched",
    version="0.9.3.post1",
    author="Original: Facebook Research, Patched by: Patrick",
    author_email="",
    description="FastText with numpy 2.x compatibility patch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/facebookresearch/fastText",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
        "pybind11>=2.2",
    ],
)

