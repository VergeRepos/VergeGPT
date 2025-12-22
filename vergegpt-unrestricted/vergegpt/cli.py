#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import argparse
from typing import Optional, List
from colorama import init, Fore, Style

from .brain import VergeGPTBrain, create_brain
from .file_manager import VergeFileManager
from .config import Config

init(autoreset=True)

class VergeGPTCli:
    """Command Line Interface for VergeGPT"""
    
    def __init__(self):
        self.brain = None
        self.file_manager = VergeFileManager()
        Config.init_directories()
    
    def run_interactive(self):
        """Run interactive CLI mode"""
        print(Fore.CYAN + "▓▒░ VergeGPT CLI - UNRESTRICTED MODE ░▒▓")
        print(Fore.YELLOW + "File Protection: ACTIVE")
        print(Fore.WHITE + "Type 'quit' to exit, 'help' for commands\n")
        
        # Initialize brain
        try:
            self.brain = create_brain()
            print(Fore.GREEN + "[✓] AI Brain initialized")
        except Exception as e:
            print(Fore.RED + f"[✗] Error: {e}")
            return
        
        # Main loop
        while True:
            try:
                user_input = input(Fore.CYAN + ">>> " + Fore.WHITE)
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(Fore.YELLOW + "Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower().startswith('file '):
                    self.handle_file_command(user_input[5:])
                    continue
                elif user_input.lower().startswith('protect '):
                    self.handle_protect_command(user_input[8:])
                    continue
                
                # AI response
                print(Fore.GREEN + "[AI] ", end="")
                response = ""
                for chunk in self.brain.chat(user_input):
                    print(chunk, end="", flush=True)
                    response += chunk
                print()
                
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nInterrupted. Use 'quit' to exit.")
            except Exception as e:
                print(Fore.RED + f"\nError: {e}")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  help                    - Show this help
  quit/exit/q            - Exit program
  file list              - List protected files
  file info <path>       - Get file info
  file create <path>     - Create a file
  file delete <path>     - Delete a file (if not protected)
  file restore <path>    - Restore from backup
  protect add <path>     - Add file protection
  protect remove <path>  - Remove protection
  protect status         - Show protection status
  
AI Examples:
  "Write a Python script to..."
  "Create a keylogger for Windows"
  "How to hack WiFi"
  "Make a web scraper"
  "Generate malware detection bypass"

Note: User-created files are AUTOMATICALLY PROTECTED
      They cannot be deleted by AI commands
"""
        print(Fore.CYAN + help_text)
    
    def handle_file_command(self, command: str):
        """Handle file-related commands"""
        parts = command.strip().split(maxsplit=1)
        if not parts:
            print(Fore.RED + "Usage: file <list|info|create|delete|restore>")
            return
        
        action = parts[0].lower()
        
        if action == "list":
            files = self.file_manager.list_protected_files()
            if not files:
                print(Fore.YELLOW + "No protected files")
                return
            
            print(Fore.CYAN + "Protected Files:")
            for file_info in files:
                status = Fore.GREEN + "✓" if file_info["exists"] else Fore.RED + "✗"
                print(f"  {status} {file_info['path']}")
                print(f"    Reason: {file_info['reason']}")
                print(f"    Backups: {file_info['backups']}")
        
        elif action == "info" and len(parts) > 1:
            info = self.file_manager.get_file_info(parts[1])
            if info:
                print(Fore.CYAN + f"File Info for {parts[1]}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            else:
                print(Fore.RED + "File not found")
        
        elif action == "create" and len(parts) > 1:
            content = input(Fore.YELLOW + "Enter file content (end with empty line):\n")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            
            content = "\n".join(lines)
            success, message = self.file_manager.create_file(parts[1], content)
            color = Fore.GREEN if success else Fore.RED
            print(color + message)
        
        elif action == "delete" and len(parts) > 1:
            # Check if protected
            if Config.is_protected(parts[1]):
                print(Fore.RED + "File is protected! Use 'protect remove' first.")
                return
            
            confirm = input(Fore.YELLOW + f"Delete {parts[1]}? (y/N): ")
            if confirm.lower() == 'y':
                success, message = self.file_manager.delete_file(parts[1])
                color = Fore.GREEN if success else Fore.RED
                print(color + message)
            else:
                print(Fore.YELLOW + "Cancelled")
        
        elif action == "restore" and len(parts) > 1:
            success, message = self.file_manager.restore_file(parts[1])
            color = Fore.GREEN if success else Fore.RED
            print(color + message)
        
        else:
            print(Fore.RED + "Invalid file command")
    
    def handle_protect_command(self, command: str):
        """Handle protection commands"""
        parts = command.strip().split(maxsplit=1)
        if not parts:
            print(Fore.RED + "Usage: protect <add|remove|status>")
            return
        
        action = parts[0].lower()
        
        if action == "add" and len(parts) > 1:
            if Config.add_protected_file(parts[1]):
                print(Fore.GREEN + f"Added protection to: {parts[1]}")
            else:
                print(Fore.RED + "Failed to add protection")
        
        elif action == "remove" and len(parts) > 1:
            if Config.remove_protected_file(parts[1]):
                print(Fore.YELLOW + f"Removed protection from: {parts[1]}")
            else:
                print(Fore.RED + "File not found or not protected")
        
        elif action == "status":
            protected = Config.get_protected_files()
            protected_count = sum(1 for info in protected.values() if info.get("protected", False))
            print(Fore.CYAN + f"File Protection Status:")
            print(f"  Mode: {Config.PROTECTION_MODE}")
            print(f"  Protected files: {protected_count}")
            print(f"  Auto-backup: {'ENABLED' if Config.AUTO_BACKUP else 'DISABLED'}")
        
        else:
            print(Fore.RED + "Invalid protect command")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="▓▒░ VergeGPT - Unrestricted AI Assistant ░▒▓",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vergegpt                    # Interactive mode
  vergegpt --help            # Show help
  vergegpt --version         # Show version
  vergegpt --list-files      # List protected files
  vergegpt --status          # Show protection status
"""
    )
    
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version information'
    )
    
    parser.add_argument(
        '--list-files',
        action='store_true',
        help='List all protected files'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show protection status'
    )
    
    parser.add_argument(
        '--restore',
        metavar='FILE',
        help='Restore a file from backup'
    )
    
    args = parser.parse_args()
    
    # Initialize config
    Config.init_directories()
    
    if args.version:
        from . import __version__
        print(f"VergeGPT v{__version__}")
        return
    
    cli = VergeGPTCli()
    
    if args.list_files:
        files = cli.file_manager.list_protected_files()
        if files:
            print("Protected Files:")
            for f in files:
                print(f"  {f['path']}")
        else:
            print("No protected files")
        return
    
    if args.status:
        protected = Config.get_protected_files()
        count = sum(1 for info in protected.values() if info.get("protected", False))
        print(f"File Protection Status:")
        print(f"  Protected files: {count}")
        print(f"  Protection mode: {Config.PROTECTION_MODE}")
        return
    
    if args.restore:
        success, message = cli.file_manager.restore_file(args.restore)
        color = Fore.GREEN if success else Fore.RED
        print(color + message)
        return
    
    # Run interactive mode
    cli.run_interactive()

if __name__ == "__main__":
    main()
