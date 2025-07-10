#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.thor_main import main

if __name__ == '__main__':
    main()
