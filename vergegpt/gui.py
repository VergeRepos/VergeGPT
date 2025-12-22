#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
▓▒░ VergeGPT GUI - Unrestricted AI with File Protection ░▒▓
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import datetime
from typing import Optional

from .brain import VergeGPTBrain, create_brain
from .file_manager import VergeFileManager
from .config import Config, ThemeManager

# Import GUI components
try:
    from .themes.glass import GlassButton, GlassEntry, GlassText, ModernNotebook
except ImportError:
    # Fallback to basic widgets
    class GlassButton:
        @staticmethod
        def create(master, **kwargs):
            return tk.Button(master, **kwargs)
    
    class GlassEntry:
        @staticmethod
        def create(master, **kwargs):
            return tk.Entry(master, **kwargs)
    
    class GlassText:
        @staticmethod
        def create(master, **kwargs):
            return tk.Text(master, **kwargs)
    
    class ModernNotebook(ttk.Notebook):
        pass

class VergeGPTGUI:
    """Main GUI Application"""
    
    def __init__(self, root=None):
        if root is None:
            root = tk.Tk()
        
        self.root = root
        self.setup_window()
        
        # Initialize components
        Config.init_directories()
        self.file_manager = VergeFileManager()
        self.brain = None
        
        # State variables
        self.is_streaming = False
        self.current_response = ""
        
        # Setup GUI
        self.setup_gui()
        self.check_api_key()
        
        # Start protection monitor
        self.start_protection_monitor()
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("▓▒░ VergeGPT - Unrestricted with File Protection ░▒▓")
        self.root.geometry("1400x900")
        
        # Load theme
        theme_name = ThemeManager.load_theme_preference()
        self.theme = ThemeManager.get_theme(theme_name)
        
        # Set window background
        self.root.configure(bg=self.theme['bg_dark'])
        
        # Set minimum size
        self.root.minsize(1200, 700)
    
    def setup_gui(self):
        """Setup GUI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.theme['bg_medium'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Notebook
        self.notebook = ModernNotebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tabs
        self.create_chat_tab()
        self.create_code_tab()
        self.create_files_tab()
        self.create_protection_tab()
        self.create_settings_tab()
        
        # Input area
        self.create_input_area(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header section"""
        header = tk.Frame(parent, bg=self.theme['bg_medium'])
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title = tk.Label(
            header,
            text="▓▒░ VERGEGPT - UNRESTRICTED WITH FILE PROTECTION ░▒▓",
            bg=self.theme['bg_medium'],
            fg=self.theme['primary'],
            font=('Segoe UI', 18, 'bold')
        )
        title.pack(side=tk.LEFT, padx=20)
        
        # Protection status
        self.protection_status = tk.StringVar(value="▓▒░ PROTECTION: ACTIVE ░▒▓")
        status_label = tk.Label(
            header,
            textvariable=self.protection_status,
            bg=self.theme['bg_medium'],
            fg=self.theme['success'],
            font=('Segoe UI', 10, 'bold')
        )
        status_label.pack(side=tk.RIGHT, padx=20)
    
    def create_chat_tab(self):
        """Create chat tab"""
        frame = tk.Frame(self.notebook, bg=self.theme['bg_medium'])
        
        # Chat display
        self.chat_display = GlassText.create(
            frame,
            wrap=tk.WORD,
            bg=self.theme['bg_light'],
            fg=self.theme['text'],
            font=('Consolas', 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.chat_display.yview)
        
        self.chat_display.config(state=tk.DISABLED)
        self.notebook.add(frame, text="💬 Chat")
    
    def create_code_tab(self):
        """Create code tab"""
        frame = tk.Frame(self.notebook, bg=self.theme['bg_medium'])
        self.notebook.add(frame, text="⚡ Code")
        # Implementation similar to previous versions
    
    def create_files_tab(self):
        """Create files tab with protection info"""
        frame = tk.Frame(self.notebook, bg=self.theme['bg_medium'])
        
        # Protected files list
        files_frame = tk.Frame(frame, bg=self.theme['bg_medium'])
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox
        self.files_listbox = tk.Listbox(
            files_frame,
            bg=self.theme['bg_light'],
            fg=self.theme['text'],
            font=('Consolas', 10),
            selectbackground=self.theme['primary'],
            selectforeground=self.theme['bg_dark']
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(files_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(frame, bg=self.theme['bg_medium'])
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        buttons = [
            ("🔄 Refresh", self.refresh_files_list),
            ("🔒 Protect", self.protect_selected_file),
            ("🔓 Unprotect", self.unprotect_selected_file),
            ("📊 Info", self.show_file_info),
            ("💾 Backup", self.backup_selected_file),
            ("↩️ Restore", self.restore_selected_file)
        ]
        
        for text, command in buttons:
            btn = GlassButton.create(btn_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_files_list()
        self.notebook.add(frame, text="📁 Protected Files")
    
    def create_protection_tab(self):
        """Create protection management tab"""
        frame = tk.Frame(self.notebook, bg=self.theme['bg_medium'])
        
        # Protection statistics
        stats_frame = tk.LabelFrame(
            frame,
            text="Protection Statistics",
            bg=self.theme['bg_medium'],
            fg=self.theme['text']
        )
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=10,
            bg=self.theme['bg_light'],
            fg=self.theme['text'],
            font=('Consolas', 10)
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.stats_text.config(state=tk.DISABLED)
        
        # Update stats
        self.update_protection_stats()
        
        # Protection settings
        settings_frame = tk.LabelFrame(
            frame,
            text="Protection Settings",
            bg=self.theme['bg_medium'],
            fg=self.theme['text']
        )
        settings_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Settings controls
        self.create_protection_settings(settings_frame)
        
        self.notebook.add(frame, text="🛡️ Protection")
    
    def create_protection_settings(self, parent):
        """Create protection settings controls"""
        # Auto-backup
        self.auto_backup_var = tk.BooleanVar(value=Config.AUTO_BACKUP)
        backup_check = tk.Checkbutton(
            parent,
            text="Enable Auto-Backup",
            variable=self.auto_backup_var,
            bg=self.theme['bg_medium'],
            fg=self.theme['text'],
            selectcolor=self.theme['primary'],
            command=self.update_auto_backup
        )
        backup_check.pack(anchor='w', padx=20, pady=5)
        
        # Protection mode
        mode_frame = tk.Frame(parent, bg=self.theme['bg_medium'])
        mode_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(
            mode_frame,
            text="Protection Mode:",
            bg=self.theme['bg_medium'],
            fg=self.theme['text']
        ).pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value=Config.PROTECTION_MODE)
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.mode_var,
            values=["strict", "warning", "none"],
            state="readonly",
            width=10
        )
        mode_combo.pack(side=tk.LEFT, padx=5)
        mode_combo.bind('<<ComboboxSelected>>', self.update_protection_mode)
    
    def create_settings_tab(self):
        """Create settings tab"""
        frame = tk.Frame(self.notebook, bg=self.theme['bg_medium'])
        
        # Theme selection
        theme_frame = tk.LabelFrame(
            frame,
            text="Theme",
            bg=self.theme['bg_medium'],
            fg=self.theme['text']
        )
        theme_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.theme_var = tk.StringVar(value=ThemeManager.load_theme_preference())
        
        for theme_name in ThemeManager.THEMES.keys():
            rb = tk.Radiobutton(
                theme_frame,
                text=theme_name,
                variable=self.theme_var,
                value=theme_name,
                bg=self.theme['bg_medium'],
                fg=self.theme['text'],
                selectcolor=self.theme['primary'],
                command=self.change_theme
            )
            rb.pack(anchor='w', padx=20, pady=5)
        
        # API Settings
        api_frame = tk.LabelFrame(
            frame,
            text="API Settings",
            bg=self.theme['bg_medium'],
            fg=self.theme['text']
        )
        api_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        api_btn = GlassButton.create(
            api_frame,
            text="Configure API",
            command=self.configure_api
        )
        api_btn.pack(padx=20, pady=10)
        
        self.notebook.add(frame, text="⚙️ Settings")
    
    def create_input_area(self, parent):
        """Create input area"""
        frame = tk.Frame(parent, bg=self.theme['bg_medium'])
        frame.pack(fill=tk.X, pady=(10, 0))
        
        # Input field
        self.input_entry = GlassEntry.create(
            frame,
            bg=self.theme['bg_light'],
            fg=self.theme['text'],
            font=('Segoe UI', 10)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        
        # Send button
        send_btn = GlassButton.create(
            frame,
            text="➤ Send",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        frame = tk.Frame(parent, bg=self.theme['bg_medium'])
        frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="▓▒░ Ready ░▒▓")
        status_label = tk.Label(
            frame,
            textvariable=self.status_var,
            bg=self.theme['bg_medium'],
            fg=self.theme['text_dim'],
            font=('Segoe UI', 9)
        )
        status_label.pack()
    
    def start_protection_monitor(self):
        """Start monitoring protected files"""
        self.update_protection_stats()
        self.root.after(30000, self.start_protection_monitor)  # Update every 30 seconds
    
    def update_protection_stats(self):
        """Update protection statistics"""
        protected_files = Config.get_protected_files()
        protected_count = sum(1 for info in protected_files.values() if info.get("protected", False))
        
        stats = f"""▓▒░ File Protection Statistics ░▒▓

Protected Files: {protected_count}
Auto-Backup: {'ENABLED' if Config.AUTO_BACKUP else 'DISABLED'}
Protection Mode: {Config.PROTECTION_MODE}

Last Backup: {self.get_last_backup_time()}
Audit Log: {self.get_audit_log_size()}

▓▒░ PROTECTION ACTIVE ░▒▓
All user-created files are protected from deletion.
"""
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state=tk.DISABLED)
        
        # Update status
        self.protection_status.set(f"▓▒░ PROTECTED: {protected_count} files ░▒▓")
    
    def get_last_backup_time(self):
        """Get time of last backup"""
        try:
            if Config.AUDIT_LOG.exists():
                with open(Config.AUDIT_LOG, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        if 'backup_created' in last_line:
                            return last_line[1:20]  # Extract timestamp
        except Exception:
            pass
        return "Never"
    
    def get_audit_log_size(self):
        """Get audit log size"""
        try:
            if Config.AUDIT_LOG.exists():
                size = Config.AUDIT_LOG.stat().st_size
                return f"{size} bytes"
        except Exception:
            pass
        return "0 bytes"
    
    def refresh_files_list(self):
        """Refresh protected files list"""
        self.files_listbox.delete(0, tk.END)
        files = self.file_manager.list_protected_files()
        
        for file_info in files:
            status = "✓" if file_info["exists"] else "✗"
            display = f"[{status}] {file_info['path']}"
            self.files_listbox.insert(tk.END, display)
    
    def protect_selected_file(self):
        """Protect selected file"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a file first")
            return
        
        # In real implementation, add file picker
        filepath = filedialog.askopenfilename()
        if filepath:
            if Config.add_protected_file(filepath, "user_protected"):
                messagebox.showinfo("Success", f"File protected: {filepath}")
                self.refresh_files_list()
                self.update_protection_stats()
            else:
                messagebox.showerror("Error", "Failed to protect file")
    
    def unprotect_selected_file(self):
        """Remove protection from selected file"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a file first")
            return
        
        item = self.files_listbox.get(selection[0])
        # Extract path from display
        path = item.split("] ")[1] if "] " in item else item
        
        if messagebox.askyesno("Confirm", f"Remove protection from:\n{path}?"):
            if Config.remove_protected_file(path):
                messagebox.showinfo("Success", "Protection removed")
                self.refresh_files_list()
                self.update_protection_stats()
            else:
                messagebox.showerror("Error", "Failed to remove protection")
    
    def show_file_info(self):
        """Show info for selected file"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a file first")
            return
        
        item = self.files_listbox.get(selection[0])
        path = item.split("] ")[1] if "] " in item else item
        
        info = self.file_manager.get_file_info(path)
        if info:
            info_text = "▓▒░ File Information ░▒▓\n\n"
            for key, value in info.items():
                info_text += f"{key}: {value}\n"
            
            messagebox.showinfo("File Info", info_text)
        else:
            messagebox.showerror("Error", "File not found")
    
    def backup_selected_file(self):
        """Create backup of selected file"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a file first")
            return
        
        item = self.files_listbox.get(selection[0])
        path = item.split("] ")[1] if "] " in item else item
        
        Config._create_backup(path, Config._calculate_file_hash(path))
        messagebox.showinfo("Success", "Backup created")
        self.update_protection_stats()
    
    def restore_selected_file(self):
        """Restore selected file from backup"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a file first")
            return
        
        item = self.files_listbox.get(selection[0])
        path = item.split("] ")[1] if "] " in item else item
        
        if self.file_manager.restore_file(path)[0]:
            messagebox.showinfo("Success", "File restored from backup")
            self.update_protection_stats()
        else:
            messagebox.showerror("Error", "No backup found")
    
    def update_auto_backup(self):
        """Update auto-backup setting"""
        Config.AUTO_BACKUP = self.auto_backup_var.get()
        messagebox.showinfo("Settings Updated", f"Auto-backup: {'ENABLED' if Config.AUTO_BACKUP else 'DISABLED'}")
    
    def update_protection_mode(self, event=None):
        """Update protection mode"""
        Config.PROTECTION_MODE = self.mode_var.get()
        messagebox.showinfo("Settings Updated", f"Protection mode: {Config.PROTECTION_MODE}")
        self.update_protection_stats()
    
    def change_theme(self):
        """Change application theme"""
        theme_name = self.theme_var.get()
        ThemeManager.save_theme_preference(theme_name)
        messagebox.showinfo("Theme Changed", f"Theme changed to {theme_name}\nRestart to apply changes.")
    
    def check_api_key(self):
        """Check and configure API key"""
        try:
            self.brain = create_brain()
            self.status_var.set("▓▒░ AI Ready - Unrestricted Mode ░▒▓")
        except Exception as e:
            self.status_var.set("▓▒░ API Key Required ░▒▓")
            if messagebox.askyesno("API Key", "API key not found. Configure now?"):
                self.configure_api()
    
    def configure_api(self):
        """Configure API key dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("▓▒░ Configure API Key ░▒▓")
        dialog.geometry("500x200")
        dialog.configure(bg=self.theme['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Implementation similar to previous versions
        # ... (API configuration dialog)
    
    def send_message(self, event=None):
        """Send message to AI"""
        if self.is_streaming or not self.brain:
            return
        
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.input_entry.delete(0, tk.END)
        self.add_chat_message("User", message)
        
        # Start AI response in thread
        self.is_streaming = True
        self.current_response = ""
        thread = threading.Thread(target=self.get_ai_response, args=(message,))
        thread.daemon = True
        thread.start()
    
    def get_ai_response(self, message):
        """Get AI response in background thread"""
        try:
            response = ""
            for chunk in self.brain.chat(message):
                response += chunk
                self.root.after(0, self.update_chat_stream, chunk)
            
            self.root.after(0, self.finish_chat_response, response)
        except Exception as e:
            self.root.after(0, self.add_chat_message, "System", f"Error: {str(e)}")
        finally:
            self.root.after(0, self.finish_streaming)
    
    def update_chat_stream(self, chunk):
        """Update chat with streaming response"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, chunk)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.current_response += chunk
    
    def finish_chat_response(self, full_response):
        """Finish chat response"""
        # Add timestamp and formatting
        self.add_chat_message("AI", full_response)
    
    def finish_streaming(self):
        """Finish streaming"""
        self.is_streaming = False
        self.status_var.set("▓▒░ Ready ░▒▓")
    
    def add_chat_message(self, sender, message):
        """Add formatted message to chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if sender == "User":
            prefix = f"\n▓▒░ [{timestamp}] User: "
            tag = "user"
        elif sender == "AI":
            prefix = f"\n▓▒░ [{timestamp}] VergeGPT: "
            tag = "ai"
        else:
            prefix = f"\n▓▒░ [{timestamp}] System: "
            tag = "system"
        
        self.chat_display.insert(tk.END, f"{prefix}{message} ░▒▓\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main GUI entry point"""
    root = tk.Tk()
    app = VergeGPTGUI(root)
    app.run()

if __name__ == "__main__":
    main()
