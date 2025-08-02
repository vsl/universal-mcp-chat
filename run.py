#!/usr/bin/env python3
"""
Convenience launcher script for MCP Agent Chat.
This script should be run from the project root directory.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main function
from run_chat import main

if __name__ == "__main__":
    main()
