#!/usr/bin/env python3
"""
Setup script for Sovereign File Tracker (SFT)
"""

from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sft",
    version="0.1.0",
    author="Sovereign File Tracker",
    description="A command-line tool for tracking and managing file lineage with relational linking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sovereign-file-tracker",
    packages=find_packages(),
    py_modules=['sft'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sft=sft:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="file tracking, version control, file management, command line",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sovereign-file-tracker/issues",
        "Source": "https://github.com/yourusername/sovereign-file-tracker",
    },
)
