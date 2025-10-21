"""
Startup module to configure sys.path before any imports.
This must be imported first in main.py.
"""

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
