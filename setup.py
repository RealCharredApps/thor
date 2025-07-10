# setup.py
from setuptools import setup, find_packages

setup(
    name="thor-ai",
    version="2.0.0",
    description="Advanced AI Development Assistant with Swarm Capabilities",
    author="RealCharredApps",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.25.0",
        "asyncio",
        "aiofiles",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "sqlalchemy>=2.0.0",
        "aiosqlite>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "thor=src.thor_main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)