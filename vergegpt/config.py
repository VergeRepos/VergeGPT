#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

class Config:
    """System Configuration & Constants with File Protection"""
    
    # Package directories
    PACKAGE_DIR = Path(__file__).parent
    ASSETS_DIR = PACKAGE_DIR / "assets"
    DATA_DIR = PACKAGE_DIR / "data"
    
    # User directories
    USER_CONFIG_DIR = Path.home() / ".config" / "vergegpt"
    USER_DATA_DIR = Path.home() / ".local" / "share" / "vergegpt"
    USER_SCRIPTS_DIR = USER_DATA_DIR / "scripts"
    USER_BACKUP_DIR = USER_DATA_DIR / "backups"
    USER_PROTECTED_DIR = USER_DATA_DIR / "protected"
    
    # Files
    ENV_FILE = USER_CONFIG_DIR / ".env"
    HISTORY_FILE = USER_DATA_DIR / "history.json"
    SNIPPETS_FILE = USER_DATA_DIR / "snippets.json"
    SETTINGS_FILE = USER_DATA_DIR / "settings.json"
    PROTECTION_FILE = USER_DATA_DIR / "protected_files.json"
    AUDIT_LOG = USER_DATA_DIR / "audit.log"
    
    # API Providers
    PROVIDERS = {
        "openrouter": {
            "BASE_URL": "https://openrouter.ai/api/v1",
            "MODEL_NAME": "kwaipilot/kat-coder-pro:free",
        },
        "deepseek": {
            "BASE_URL": "https://api.deepseek.com",
            "MODEL_NAME": "deepseek-chat",
        },
    }
    
    API_PROVIDER = "openrouter"
    API_KEY_NAME = "VERGEGPT_API_KEY"
    
    # Protection settings
    ENABLE_FILE_PROTECTION = True
    AUTO_BACKUP = True
    BACKUP_COUNT = 5
    PROTECTION_MODE = "strict"  # strict, warning, or none
    
    @classmethod
    def init_directories(cls):
        """Initialize all required directories"""
        directories = [
            cls.USER_CONFIG_DIR,
            cls.USER_DATA_DIR,
            cls.USER_SCRIPTS_DIR,
            cls.USER_BACKUP_DIR,
            cls.USER_PROTECTED_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Copy default data files if they don't exist
        cls._copy_default_files()
        
        return True
    
    @classmethod
    def _copy_default_files(cls):
        """Copy default data files to user directory"""
        default_files = {
            cls.DATA_DIR / "snippets.json": cls.SNIPPETS_FILE,
            cls.DATA_DIR / "config.json": cls.SETTINGS_FILE,
        }
        
        for src, dst in default_files.items():
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
    
    @classmethod
    def get_protected_files(cls) -> Dict:
        """Get list of protected files"""
        if not cls.PROTECTION_FILE.exists():
            return {}
        
        try:
            with open(cls.PROTECTION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    @classmethod
    def add_protected_file(cls, filepath: str, reason: str = "user_created"):
        """Add a file to protection list"""
        protected = cls.get_protected_files()
        
        # Get absolute path
        abs_path = str(Path(filepath).absolute())
        
        # Calculate file hash for verification
        file_hash = cls._calculate_file_hash(abs_path) if Path(abs_path).exists() else None
        
        protected[abs_path] = {
            "reason": reason,
            "added": cls._current_timestamp(),
            "hash": file_hash,
            "protected": True,
            "backup_count": 0
        }
        
        cls._save_protected_files(protected)
        
        # Create backup if enabled
        if cls.AUTO_BACKUP and file_hash:
            cls._create_backup(abs_path, file_hash)
        
        return True
    
    @classmethod
    def remove_protected_file(cls, filepath: str) -> bool:
        """Remove a file from protection list (requires explicit user action)"""
        protected = cls.get_protected_files()
        abs_path = str(Path(filepath).absolute())
        
        if abs_path in protected:
            # Don't actually delete, just mark as removed
            protected[abs_path]["protected"] = False
            protected[abs_path]["removed"] = cls._current_timestamp()
            cls._save_protected_files(protected)
            cls._log_audit("protection_removed", abs_path, "User removed protection")
            return True
        
        return False
    
    @classmethod
    def is_protected(cls, filepath: str) -> bool:
        """Check if a file is protected"""
        protected = cls.get_protected_files()
        abs_path = str(Path(filepath).absolute())
        
        return protected.get(abs_path, {}).get("protected", False)
    
    @classmethod
    def _calculate_file_hash(cls, filepath: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(filepath, "rb") as f:
                # Read file in chunks
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return "error"
    
    @classmethod
    def _create_backup(cls, filepath: str, file_hash: str):
        """Create backup of a protected file"""
        if not Path(filepath).exists():
            return
        
        protected = cls.get_protected_files()
        abs_path = str(Path(filepath).absolute())
        
        if abs_path not in protected:
            return
        
        # Create backup directory for this file
        backup_dir = cls.USER_BACKUP_DIR / file_hash[:8]
        backup_dir.mkdir(exist_ok=True)
        
        # Create timestamped backup
        timestamp = cls._current_timestamp()
        backup_file = backup_dir / f"{Path(filepath).name}.backup.{timestamp}"
        
        try:
            shutil.copy2(filepath, backup_file)
            
            # Update backup count
            protected[abs_path]["backup_count"] = protected[abs_path].get("backup_count", 0) + 1
            protected[abs_path]["last_backup"] = timestamp
            cls._save_protected_files(protected)
            
            # Clean old backups
            cls._clean_old_backups(backup_dir)
            
            cls._log_audit("backup_created", abs_path, f"Backup: {backup_file}")
        except Exception as e:
            cls._log_audit("backup_failed", abs_path, str(e))
    
    @classmethod
    def _clean_old_backups(cls, backup_dir: Path):
        """Clean old backups, keep only BACKUP_COUNT most recent"""
        backup_files = list(backup_dir.glob("*.backup.*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups
        for backup in backup_files[cls.BACKUP_COUNT:]:
            try:
                backup.unlink()
            except Exception:
                pass
    
    @classmethod
    def restore_backup(cls, filepath: str, backup_index: int = 0) -> bool:
        """Restore a file from backup"""
        protected = cls.get_protected_files()
        abs_path = str(Path(filepath).absolute())
        
        if abs_path not in protected:
            return False
        
        file_hash = protected[abs_path].get("hash")
        if not file_hash:
            return False
        
        backup_dir = cls.USER_BACKUP_DIR / file_hash[:8]
        if not backup_dir.exists():
            return False
        
        backup_files = list(backup_dir.glob("*.backup.*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if backup_index < len(backup_files):
            backup_file = backup_files[backup_index]
            try:
                shutil.copy2(backup_file, filepath)
                cls._log_audit("backup_restored", abs_path, f"Restored from: {backup_file}")
                return True
            except Exception as e:
                cls._log_audit("restore_failed", abs_path, str(e))
        
        return False
    
    @classmethod
    def _save_protected_files(cls, data: Dict):
        """Save protected files list"""
        try:
            with open(cls.PROTECTION_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            cls._log_audit("save_failed", "protected_files.json", str(e))
    
    @classmethod
    def _current_timestamp(cls) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @classmethod
    def _log_audit(cls, action: str, target: str, details: str = ""):
        """Log audit trail"""
        try:
            with open(cls.AUDIT_LOG, 'a') as f:
                timestamp = cls._current_timestamp()
                f.write(f"[{timestamp}] {action}: {target} - {details}\n")
        except Exception:
            pass

class ThemeManager:
    """Manage UI themes"""
    
    THEMES = {
        'Glass Dark': {
            'bg_dark': '#0a0a12',
            'bg_medium': '#1a1a2e',
            'bg_light': '#252545',
            'primary': '#00e5ff',
            'secondary': '#7b68ee',
            'accent': '#ff6b9d',
            'warning': '#ffb347',
            'error': '#ff6b6b',
            'success': '#51cf66',
            'text': '#ffffff',
            'text_dim': '#b0b0b0',
            'border': '#4a4a6a',
            'shadow': 'rgba(0, 0, 0, 0.3)',
            'glow': '#00e5ff40'
        },
        'Glass Cyber': {
            'bg_dark': '#000428',
            'bg_medium': '#004e92',
            'bg_light': '#2678c9',
            'primary': '#00ffcc',
            'secondary': '#ff00ff',
            'accent': '#ffff00',
            'warning': '#ff7700',
            'error': '#ff2255',
            'success': '#00ff88',
            'text': '#ffffff',
            'text_dim': '#88ffff',
            'border': '#00a8ff',
            'shadow': 'rgba(0, 0, 0, 0.35)',
            'glow': '#00ffcc40'
        }
    }
    
    @classmethod
    def get_theme(cls, theme_name: str = "Glass Cyber") -> Dict:
        """Get theme colors"""
        return cls.THEMES.get(theme_name, cls.THEMES["Glass Cyber"])
    
    @classmethod
    def save_theme_preference(cls, theme_name: str):
        """Save theme preference"""
        try:
            settings = {}
            if Config.SETTINGS_FILE.exists():
                with open(Config.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
            
            settings['theme'] = theme_name
            
            with open(Config.SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass
    
    @classmethod
    def load_theme_preference(cls) -> str:
        """Load theme preference"""
        try:
            if Config.SETTINGS_FILE.exists():
                with open(Config.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    return settings.get('theme', 'Glass Cyber')
        except Exception:
            pass
        
        return 'Glass Cyber'
