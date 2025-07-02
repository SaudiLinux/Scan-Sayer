#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="scansayer",
    version="1.0.0",
    author="Saudi Linux",
    author_email="SayerLinux@gmail.com",
    description="ماسح أمني آلي مفتوح المصدر مصمم لاكتشاف الأصول وفحص الثغرات الأمنية",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SaudiLinux/ScanSayer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "scansayer=scansayer:main",
        ],
    },
)