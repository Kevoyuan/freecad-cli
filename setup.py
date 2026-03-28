# -*- coding: utf-8 -*-
"""
FreeCAD CLI Setup Script
========================

Installation configuration script for installing freecad-cli package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="freecad-cli",
    version="1.0.0",
    author="MiniMax Agent",
    author_email="agent@minimax.io",
    description="FreeCAD Command Line Interface - AI-friendly CAD automation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MiniMax-AI/freecad-cli",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v2.1 (LGPLv2.1)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: CAD",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "all": [
            "click>=8.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "freecad-cli=freecad_cli.core:main",
        ],
    },
    package_data={
        "freecad_cli": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
)
