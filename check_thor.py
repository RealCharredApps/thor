#!/usr/bin/env python3
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")
print(f"Path: {sys.path}")

print("\nChecking imports:")
try:
    import anthropic
    print("✅ anthropic")
except ImportError:
    print("❌ anthropic - run: pip install anthropic")

try:
    import click
    print("✅ click")
except ImportError:
    print("❌ click - run: pip install click")

try:
    import rich
    print("✅ rich")
except ImportError:
    print("❌ rich - run: pip install rich")

try:
    import yaml
    print("✅ yaml")
except ImportError:
    print("❌ yaml - run: pip install pyyaml")

try:
    import dotenv
    print("✅ dotenv")
except ImportError:
    print("❌ dotenv - run: pip install python-dotenv")

try:
    import aiofiles
    print("✅ aiofiles")
except ImportError:
    print("❌ aiofiles - run: pip install aiofiles")

print("\nChecking THOR modules:")
try:
    from src.thor_main import main
    print("✅ THOR main module")
except Exception as e:
    print(f"❌ THOR main module: {e}")

try:
    from src.core.thor_client import ThorClient
    print("✅ THOR client module")
except Exception as e:
    print(f"❌ THOR client module: {e}")
