#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="vergegpt-unrestricted",
    version="2.0.0",
    author="Verge",
    author_email="verge@vergegpt.dev",
    description="Unrestricted AI Assistant with File Protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/verge/vergegpt",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "vergegpt": [
            "assets/*",
            "data/*",
            "themes/*.py",
            "themes/__init__.py"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vergegpt=vergegpt.cli:main",
            "vergegpt-gui=vergegpt.gui:main",
        ],
    },
    keywords=[
        "ai", "assistant", "unrestricted", "hacker", "security",
        "automation", "development", "chatgpt", "llm"
    ],
    project_urls={
        "Bug Reports": "https://github.com/verge/vergegpt/issues",
        "Source": "https://github.com/verge/vergegpt",
    },
)
