#!/usr/bin/env python
from io import open
from setuptools import setup

"""
:authors: g7AzaZLO
:license: MIT
:copyright: (c) 2025 g7AzaZLO
"""

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = "0.1.2"

setup(
    name="fastapi_ast_inference",
    version=version,
    author="g7AzaZLO",
    author_email="maloymeee@yandex.ru",
    description="Automatic response model inference for FastAPI using AST analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/g7AzaZLO/fastapi_ast_inference",
    download_url=f"https://github.com/g7AzaZLO/fastapi_ast_inference/archive/refs/tags/v{version}.zip".format(version),
    license="MIT",
    packages=["fastapi_ast_inference"],
    install_requires=[
    "fastapi>=0.100.0",
    "pydantic>=2.0.0",
    ],
    classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Web Environment",
    "Framework :: FastAPI",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",
    ],

)
