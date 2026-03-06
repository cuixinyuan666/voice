'''Sidekick UI

This module implements the modern-style desktop UI for Sidekick, a voice-controlled keyboard and mouse tool.

Copyright (C) 2021 UT-Battelle - Created by Sean Oesch
Modified by [Your Name] to add modern UI

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

import customtkinter as ctk
import threading
import queue
import time
from parsepackage import parser

class SidekickUI:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Sidekick - Voice Controlled Keyboard and Mouse")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # Create a queue for communication between threads
        self.queue = queue.Queue()

        # Initialize UI components
        self.create_ui()

        # Initialize state variables
        self.running = True
        self.paused = False
        self.current_state = "命令"
        self.log_messages = []

    def create_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Create status frame
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill=ctk.X, pady=(0, 10))

        # Status label
        self.status_label = ctk.CTkLabel(self.status_frame, text="状态: 等待指令", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(side=ctk.LEFT, padx=10, pady=5)

        # Current state label
        self.state_label = ctk.CTkLabel(self.status_frame, text="当前模式: 命令", font=("Segoe UI", 12))
        self.state_label.pack(side=ctk.RIGHT, padx=10, pady=5)

        # Create control frame
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(fill=ctk.X, pady=(0, 10))

        # Start/Pause button
        self.start_pause_button = ctk.CTkButton(self.control_frame, text="暂停", command=self.toggle_pause, width=100)
        self.start_pause_button.pack(side=ctk.LEFT, padx=10, pady=5)

        # Clear log button
        self.clear_log_button = ctk.CTkButton(self.control_frame, text="清空日志", command=self.clear_log, width=100)
        self.clear_log_button.pack(side=ctk.RIGHT, padx=10, pady=5)

        # Create volume visualization frame
        self.volume_frame = ctk.CTkFrame(self.main_frame)
        self.volume_frame.pack(fill=ctk.X, pady=(0, 10))

        # Volume label
        self.volume_label = ctk.CTkLabel(self.volume_frame, text="麦克风音量", font=("Segoe UI", 12))
        self.volume_label.pack(padx=10, pady=(5, 0))

        # Volume bar
        self.volume_bar = ctk.CTkProgressBar(self.volume_frame, height=10)
        self.volume_bar.pack(fill=ctk.X, padx=10, pady=5)
        self.volume_bar.set(0)

        # Create log frame
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        # Log label
        self.log_label = ctk.CTkLabel(self.log_frame, text="识别日志", font=("Segoe UI", 12, "bold"))
        self.log_label.pack(padx=10, pady=(5, 0))

        # Log text box
        self.log_text = ctk.CTkTextbox(self.log_frame, font=("Segoe UI", 10))
        self.log_text.pack(fill=ctk.BOTH, expand=True, padx=10, pady=5)
        self.log_text.configure(state="disabled")

        # Create settings button
        self.settings_button = ctk.CTkButton(self.main_frame, text="设置", command=self.open_settings, width=100)
        self.settings_button.pack(side=ctk.RIGHT, padx=10, pady=5)

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.start_pause_button.configure(text="开始")
            self.status_label.configure(text="状态: 已暂停")
            # Update global pause state
            import sidekick
            sidekick.is_paused = True
            sidekick.parser.pause = True
            sidekick.parser.state = "文本"
            self.add_log_message("Sidekick 已暂停", "成功")
        else:
            self.start_pause_button.configure(text="暂停")
            self.status_label.configure(text="状态: 等待指令")
            # Update global pause state
            import sidekick
            sidekick.is_paused = False
            sidekick.parser.pause = False
            sidekick.parser.state = "命令"
            self.add_log_message("Sidekick 已开始工作", "成功")

    def clear_log(self):
        self.log_messages = []
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, ctk.END)
        self.log_text.configure(state="disabled")

    def update_volume(self, volume):
        self.volume_bar.set(volume)

    def add_log_message(self, message, status="成功"):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message} - {status}\n"
        self.log_messages.append(log_entry)
        
        # Keep only the last 50 messages
        if len(self.log_messages) > 50:
            self.log_messages = self.log_messages[-50:]
        
        # Update log text box
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, ctk.END)
        for entry in self.log_messages:
            self.log_text.insert(ctk.END, entry)
        self.log_text.configure(state="disabled")
        self.log_text.see(ctk.END)

    def update_state(self, state):
        self.current_state = state
        self.state_label.configure(text=f"当前模式: {state}")

    def open_settings(self):
        # Create settings window
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Sidekick 设置")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)

        # Create settings frame
        settings_frame = ctk.CTkFrame(settings_window)
        settings_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Model path setting
        model_path_frame = ctk.CTkFrame(settings_frame)
        model_path_frame.pack(fill=ctk.X, pady=(0, 10))

        model_path_label = ctk.CTkLabel(model_path_frame, text="Vosk 模型路径:", font=("Segoe UI", 12))
        model_path_label.pack(side=ctk.LEFT, padx=10, pady=5)

        model_path_entry = ctk.CTkEntry(model_path_frame, placeholder_text="model_cn")
        model_path_entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=10, pady=5)

        # Sensitivity setting
        sensitivity_frame = ctk.CTkFrame(settings_frame)
        sensitivity_frame.pack(fill=ctk.X, pady=(0, 10))

        sensitivity_label = ctk.CTkLabel(sensitivity_frame, text="键鼠操作灵敏度:", font=("Segoe UI", 12))
        sensitivity_label.pack(side=ctk.LEFT, padx=10, pady=5)

        sensitivity_slider = ctk.CTkSlider(sensitivity_frame, from_=1, to=10, number_of_steps=9)
        sensitivity_slider.set(5)
        sensitivity_slider.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=10, pady=5)

        # Command alias setting
        alias_frame = ctk.CTkFrame(settings_frame)
        alias_frame.pack(fill=ctk.X, pady=(0, 10))

        alias_label = ctk.CTkLabel(alias_frame, text="自定义语音指令别名:", font=("Segoe UI", 12))
        alias_label.pack(padx=10, pady=(5, 0))

        alias_text = ctk.CTkTextbox(alias_frame, height=100, font=("Segoe UI", 10))
        alias_text.pack(fill=ctk.X, padx=10, pady=5)

        # Load existing settings
        self.load_settings(model_path_entry, sensitivity_slider, alias_text)

        # Save button
        save_button = ctk.CTkButton(settings_frame, text="保存设置", width=100, command=lambda: self.save_settings(model_path_entry, sensitivity_slider, alias_text, settings_window))
        save_button.pack(side=ctk.RIGHT, padx=10, pady=5)

    def load_settings(self, model_path_entry, sensitivity_slider, alias_text):
        # Load settings from file if it exists
        import json
        import os
        
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                if "model_path" in settings:
                    model_path_entry.insert(0, settings["model_path"])
                if "sensitivity" in settings:
                    sensitivity_slider.set(settings["sensitivity"])
                if "command_aliases" in settings:
                    alias_text.insert(1.0, settings["command_aliases"])
            except Exception as e:
                print(f"加载设置失败: {e}")

    def save_settings(self, model_path_entry, sensitivity_slider, alias_text, settings_window):
        # Save settings to file
        import json
        import os
        
        settings = {
            "model_path": model_path_entry.get() or "model_cn",
            "sensitivity": sensitivity_slider.get(),
            "command_aliases": alias_text.get(1.0, ctk.END)
        }
        
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # Show success message
            success_label = ctk.CTkLabel(settings_window, text="设置保存成功！", text_color="green")
            success_label.pack(pady=5)
            settings_window.after(2000, success_label.destroy)
        except Exception as e:
            # Show error message
            error_label = ctk.CTkLabel(settings_window, text=f"保存设置失败: {e}", text_color="red")
            error_label.pack(pady=5)
            settings_window.after(2000, error_label.destroy)

    def run(self):
        # Start the UI loop
        self.root.mainloop()

    def stop(self):
        self.running = False
        self.root.quit()

if __name__ == "__main__":
    ui = SidekickUI()
    ui.run()
