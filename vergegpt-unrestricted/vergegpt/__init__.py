
## **5. `vergegpt/__init__.py`**
"""
▓▒░ VergeGPT - Unrestricted AI Assistant ░▒▓
Version: 2.0.0
Author: Verge
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Verge"
__license__ = "MIT"

from .brain import VergeGPTBrain
from .file_manager import VergeFileManager, ProtectedFileManager
from .config import Config, ThemeManager
from .gui import VergeGPTGUI
from .cli import VergeGPTCli

__all__ = [
    "VergeGPTBrain",
    "VergeFileManager",
    "ProtectedFileManager",
    "Config",
    "ThemeManager",
    "VergeGPTGUI",
    "VergeGPTCli"
]
