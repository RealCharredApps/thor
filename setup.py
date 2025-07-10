# thor/setup.py (Updated)
from setuptools import setup, find_packages
import os

# Read requirements
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# Read long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="thor-ai-assistant",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="THOR AI Development Assistant with Swarm Capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RealCharredApps/thor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "pre-commit>=2.20",
        ],
        "ui": [
            "streamlit>=1.28",
            "gradio>=3.40",
            "flask>=2.3",
        ],
        "full": [
            "streamlit>=1.28",
            "gradio>=3.40",
            "flask>=2.3",
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "pre-commit>=2.20",
        ],
    },
    entry_points={
        "console_scripts": [
            "thor=thor_main:main",
            "thor-interactive=thor_main:main",
            "thor-swarm=swarm_cli:main",
        ],
    },
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
    include_package_data=True,
    zip_safe=False,
)