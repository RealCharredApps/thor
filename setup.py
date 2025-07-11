# setup.py - CORRECTED VERSION
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="thor-ai",
    version="2.0.0",
    description="Advanced AI Development Assistant with Swarm Capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RealCharredApps",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        "anthropic>=0.25.0",
        "aiofiles>=23.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "sqlalchemy>=2.0.0",
        "aiosqlite>=0.19.0",
        "psutil>=5.9.0",
        "watchdog>=3.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "asyncio-throttle>=1.0.2",
        "prompt-toolkit>=3.0.0",
        "websockets>=11.0.0",
        "uvloop>=0.17.0",
        "orjson>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "thor=thor_main:main",
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
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)