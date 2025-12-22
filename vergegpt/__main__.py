#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
▓▒░ VergeGPT - Main Entry Point ░▒▓
"""

import sys
import argparse

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="▓▒░ VergeGPT - Unrestricted AI with File Protection ░▒▓"
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI interface'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Launch CLI interface'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version'
    )
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"VergeGPT v{__version__}")
        return
    
    if args.gui or (not args.cli and not args.gui):
        # Launch GUI
        try:
            from .gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI not available: {e}")
            print("Falling back to CLI...")
            args.cli = True
    
    if args.cli:
        # Launch CLI
        from .cli import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()
