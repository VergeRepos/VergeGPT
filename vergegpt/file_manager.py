#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime

from .config import Config

class ProtectedFileManager:
    """File manager with protection against deletion"""
    
    def __init__(self):
        Config.init_directories()
        self.protected_files = Config.get_protected_files()
    
    def create_file(self, filepath: str, content: str, 
                   language: str = None, protect: bool = True) -> Tuple[bool, str]:
        """Create a file with optional protection"""
        try:
            # Ensure directory exists
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Apply protection if requested
            if protect:
                Config.add_protected_file(str(filepath), "user_created")
            
            return True, f"File created: {filepath}"
            
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def delete_file(self, filepath: str, force: bool = False) -> Tuple[bool, str]:
        """Delete a file with protection check"""
        filepath = Path(filepath).absolute()
        
        # Check if file is protected
        if Config.is_protected(str(filepath)) and not force:
            return False, f"Cannot delete protected file: {filepath}"
        
        try:
            if filepath.exists():
                # Create backup before deletion if protected
                if Config.is_protected(str(filepath)):
                    Config._create_backup(str(filepath), 
                                        Config._calculate_file_hash(str(filepath)))
                
                # Remove from protection list
                Config.remove_protected_file(str(filepath))
                
                # Delete the file
                if filepath.is_dir():
                    shutil.rmtree(filepath)
                else:
                    filepath.unlink()
                
                Config._log_audit("file_deleted", str(filepath), "User deleted")
                return True, f"File deleted: {filepath}"
            else:
                return False, f"File not found: {filepath}"
                
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def move_file(self, src: str, dst: str, protect: bool = True) -> Tuple[bool, str]:
        """Move a file with protection handling"""
        src_path = Path(src).absolute()
        dst_path = Path(dst).absolute()
        
        # Check if source is protected
        was_protected = Config.is_protected(str(src_path))
        
        try:
            # Move the file
            shutil.move(str(src_path), str(dst_path))
            
            # Update protection if needed
            if was_protected:
                Config.remove_protected_file(str(src_path))
                if protect:
                    Config.add_protected_file(str(dst_path), "moved_from_protected")
            
            Config._log_audit("file_moved", f"{src} -> {dst}")
            return True, f"File moved: {src} -> {dst}"
            
        except Exception as e:
            return False, f"Error moving file: {str(e)}"
    
    def copy_file(self, src: str, dst: str, protect: bool = True) -> Tuple[bool, str]:
        """Copy a file with optional protection"""
        src_path = Path(src).absolute()
        dst_path = Path(dst).absolute()
        
        try:
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            
            # Apply protection to copy if requested
            if protect:
                Config.add_protected_file(str(dst_path), "copied_file")
            
            Config._log_audit("file_copied", f"{src} -> {dst}")
            return True, f"File copied: {src} -> {dst}"
            
        except Exception as e:
            return False, f"Error copying file: {str(e)}"
    
    def list_protected_files(self) -> List[Dict]:
        """List all protected files"""
        protected = Config.get_protected_files()
        result = []
        
        for path, info in protected.items():
            if info.get("protected", False):
                file_path = Path(path)
                result.append({
                    "path": path,
                    "reason": info.get("reason", "unknown"),
                    "added": info.get("added", ""),
                    "exists": file_path.exists(),
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                    "backups": info.get("backup_count", 0)
                })
        
        return result
    
    def restore_file(self, filepath: str, backup_index: int = 0) -> Tuple[bool, str]:
        """Restore a file from backup"""
        if Config.restore_backup(filepath, backup_index):
            # Re-protect the restored file
            Config.add_protected_file(filepath, "restored_from_backup")
            return True, f"File restored from backup: {filepath}"
        else:
            return False, f"No backup found for: {filepath}"
    
    def get_file_info(self, filepath: str) -> Optional[Dict]:
        """Get information about a file including protection status"""
        filepath = Path(filepath).absolute()
        
        if not filepath.exists():
            return None
        
        protected = Config.is_protected(str(filepath))
        protected_info = Config.get_protected_files().get(str(filepath), {})
        
        return {
            "path": str(filepath),
            "exists": True,
            "size": filepath.stat().st_size,
            "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            "protected": protected,
            "protection_reason": protected_info.get("reason", ""),
            "protection_date": protected_info.get("added", ""),
            "backup_count": protected_info.get("backup_count", 0),
            "last_backup": protected_info.get("last_backup", ""),
            "hash": protected_info.get("hash", "")
        }

class VergeFileManager(ProtectedFileManager):
    """Enhanced file manager with script execution capabilities"""
    
    # Language to file extension mapping
    LANGUAGE_EXTENSIONS = {
        'python': '.py',
        'javascript': '.js',
        'typescript': '.ts',
        'java': '.java',
        'cpp': '.cpp',
        'c++': '.cpp',
        'c': '.c',
        'c#': '.cs',
        'go': '.go',
        'rust': '.rs',
        'ruby': '.rb',
        'php': '.php',
        'html': '.html',
        'css': '.css',
        'bash': '.sh',
        'shell': '.sh',
        'powershell': '.ps1',
        'batch': '.bat',
        'sql': '.sql',
        'swift': '.swift',
        'kotlin': '.kt',
        'perl': '.pl',
        'lua': '.lua',
        'r': '.r'
    }
    
    # Execution commands for different languages
    EXECUTION_COMMANDS = {
        'python': ['python', '{file}'],
        'javascript': ['node', '{file}'],
        'typescript': ['ts-node', '{file}'],
        'java': ['javac', '{file}', '&&', 'java', '{class}'],
        'cpp': ['g++', '{file}', '-o', '{exe}', '&&', '{exe}'],
        'c': ['gcc', '{file}', '-o', '{exe}', '&&', '{exe}'],
        'go': ['go', 'run', '{file}'],
        'rust': ['rustc', '{file}', '&&', '{exe}'],
        'ruby': ['ruby', '{file}'],
        'php': ['php', '{file}'],
        'bash': ['bash', '{file}'],
        'shell': ['sh', '{file}'],
        'powershell': ['powershell', '-File', '{file}'],
        'batch': ['cmd', '/c', '{file}'],
        'lua': ['lua', '{file}'],
        'perl': ['perl', '{file}']
    }
    
    def create_script(self, filename: str, content: str, 
                     language: str = None, protect: bool = True) -> Tuple[bool, str]:
        """Create a script file with proper extension and execution permissions"""
        # Detect language if not specified
        if not language:
            language = self.detect_language_from_content(content)
        
        # Get proper file extension
        extension = self.LANGUAGE_EXTENSIONS.get(language.lower(), '.txt')
        
        # Ensure filename has proper extension
        if not filename.endswith(extension):
            filename += extension
        
        # Use user scripts directory
        if not Path(filename).is_absolute():
            filename = Config.USER_SCRIPTS_DIR / filename
        
        # Add VergeGPT prefix if not present
        if not any(prefix in str(filename).lower() for prefix in ['verge', 'vergegpt']):
            filename = filename.parent / f"vergegpt_{filename.name}"
        
        # Add shebang for Unix-like systems if applicable
        if language in ['python', 'bash', 'shell'] and not content.startswith('#!/'):
            shebangs = {
                'python': '#!/usr/bin/env python3\n',
                'bash': '#!/bin/bash\n',
                'shell': '#!/bin/sh\n'
            }
            if language in shebangs:
                content = shebangs[language] + content
        
        # Create the file with protection
        success, message = self.create_file(str(filename), content, protect=protect)
        
        if success:
            # Make executable on Unix-like systems
            if os.name != 'nt':  # Not Windows
                os.chmod(filename, 0o755)
            
            return True, f"Script created: {filename} (Language: {language})"
        
        return False, message
    
    def execute_script(self, filename: str, timeout: int = 30) -> Tuple[bool, str]:
        """Execute a script file and return output"""
        try:
            # Read file to detect language
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            language = self.detect_language_from_content(content)
            
            if language not in self.EXECUTION_COMMANDS:
                return False, f"Cannot execute {language} scripts automatically"
            
            # Prepare execution command
            base_name = Path(filename).stem
            cmd_template = self.EXECUTION_COMMANDS[language]
            cmd = []
            
            for part in cmd_template:
                if part == '{file}':
                    cmd.append(filename)
                elif part == '{exe}':
                    cmd.append(base_name + ('.exe' if os.name == 'nt' else ''))
                elif part == '{class}':
                    cmd.append(base_name)
                else:
                    cmd.append(part)
            
            # Execute the script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(filename).parent or '.'
            )
            
            output = f"Exit Code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return True, output
            
        except subprocess.TimeoutExpired:
            return False, f"Script execution timed out after {timeout} seconds"
        except FileNotFoundError:
            return False, "Required interpreter not found. Please install the necessary runtime."
        except Exception as e:
            return False, f"Error executing script: {str(e)}"
    
    @staticmethod
    def detect_language_from_content(content: str) -> str:
        """Detect programming language from file content"""
        content_lower = content.lower()
        
        if '#!/usr/bin/env python' in content_lower or 'import ' in content_lower and ('def ' in content_lower or 'print(' in content_lower):
            return 'python'
        elif 'function' in content_lower and ('const ' in content_lower or 'let ' in content_lower or 'var ' in content_lower):
            return 'javascript'
        elif '<?php' in content_lower:
            return 'php'
        elif '<!DOCTYPE html>' in content_lower or '<html>' in content_lower:
            return 'html'
        elif '#include' in content_lower:
            if 'iostream' in content_lower or 'std::' in content_lower:
                return 'cpp'
            else:
                return 'c'
        elif 'public class' in content_lower:
            return 'java'
        elif 'package main' in content_lower or 'func main()' in content_lower:
            return 'go'
        elif 'fn main()' in content_lower:
            return 'rust'
        elif '#!/bin/bash' in content_lower:
            return 'bash'
        else:
            return 'python'  # default
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return list(self.LANGUAGE_EXTENSIONS.keys())
    
    def list_user_scripts(self) -> List[Dict]:
        """List all user scripts in scripts directory"""
        scripts = []
        
        for script_file in Config.USER_SCRIPTS_DIR.glob("**/*"):
            if script_file.is_file():
                try:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read(100)  # Read first 100 chars
                    
                    language = self.detect_language_from_content(content)
                    
                    scripts.append({
                        "name": script_file.name,
                        "path": str(script_file),
                        "language": language,
                        "size": script_file.stat().st_size,
                        "modified": datetime.fromtimestamp(script_file.stat().st_mtime),
                        "protected": Config.is_protected(str(script_file))
                    })
                except Exception:
                    continue
        
        return scripts
