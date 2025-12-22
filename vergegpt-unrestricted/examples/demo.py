#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
▓▒░ VergeGPT Demo ░▒▓
"""

from vergegpt import VergeGPTBrain, VergeFileManager, Config

def demo():
    """Demonstrate VergeGPT features"""
    print("▓▒░ VergeGPT Demo ░▒▓")
    
    # Initialize
    Config.init_directories()
    file_manager = VergeFileManager()
    
    # Create a protected file
    print("\n1. Creating a protected file...")
    content = "print('Hello from VergeGPT!')"
    success, message = file_manager.create_script("demo.py", content)
    print(f"   {message}")
    
    # Check protection
    print("\n2. Checking file protection...")
    info = file_manager.get_file_info("demo.py")
    if info and info["protected"]:
        print(f"   File is PROTECTED ✓")
        print(f"   Reason: {info['protection_reason']}")
    
    # List protected files
    print("\n3. Listing protected files...")
    files = file_manager.list_protected_files()
    for f in files:
        print(f"   {f['path']}")
    
    # Try to delete (should fail)
    print("\n4. Trying to delete protected file...")
    success, message = file_manager.delete_file("demo.py")
    if not success:
        print(f"   {message} ✓ (Protection working!)")
    
    # Remove protection and delete
    print("\n5. Removing protection and deleting...")
    Config.remove_protected_file("demo.py")
    success, message = file_manager.delete_file("demo.py")
    print(f"   {message}")
    
    print("\n▓▒░ Demo Complete ░▒▓")

if __name__ == "__main__":
    demo()
