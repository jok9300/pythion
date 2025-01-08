"""
速率限制器模块

提供API调用速率限制功能，包括：
- 配置等待时间
- 显示等待进度
- 统一的速率控制界面
"""

import time
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class RateLimitConfig:
    """速率限制配置"""
    wait_minutes: float = 1.0  # 等待时间（分钟）
    show_progress: bool = True  # 是否显示进度条

class RateLimiter:
    """API调用速率限制器"""
    
    def __init__(self, config: RateLimitConfig = None):
        """初始化速率限制器
        
        Args:
            config: 速率限制配置。如果不提供，将通过界面配置。
        """
        self.config = config or self._show_config_dialog()
        self.last_call_time = 0
        
    def _show_config_dialog(self, title="API调用间隔设置", default_minutes=1.0):
        """显示配置对话框
        
        Args:
            title: 对话框标题
            default_minutes: 默认等待时间（分钟）
            
        Returns:
            RateLimitConfig: 用户配置的速率限制设置
        """
        root = tk.Tk()
        root.title(title)
        
        # 设置窗口大小和位置
        window_width = 400
        window_height = 250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 等待时间设置
        ttk.Label(main_frame, text="请设置API调用间隔时间：").pack(pady=10)
        
        wait_minutes = tk.StringVar(value=str(default_minutes))
        ttk.Entry(main_frame, textvariable=wait_minutes).pack(pady=5)
        ttk.Label(main_frame, text="分钟").pack()
        
        # 进度显示选项
        show_progress = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="显示等待进度条",
            variable=show_progress
        ).pack(pady=10)
        
        ttk.Button(main_frame, text="确认", command=root.quit).pack(pady=20)
        
        root.mainloop()
        
        config = RateLimitConfig(
            wait_minutes=float(wait_minutes.get()),
            show_progress=show_progress.get()
        )
        
        root.destroy()
        return config
    
    def update_config(self, config: RateLimitConfig = None, show_dialog: bool = True, default_minutes: float = None):
        """更新速率限制配置
        
        Args:
            config: 新的配置。如果不提供且show_dialog为True，将通过界面配置。
            show_dialog: 是否显示配置对话框
            default_minutes: 对话框中的默认等待时间
        """
        if config:
            self.config = config
        elif show_dialog:
            self.config = self._show_config_dialog(
                title="更新API调用间隔设置",
                default_minutes=default_minutes or self.config.wait_minutes
            )
    
    def wait(self, custom_message: str = None):
        """等待指定时间
        
        Args:
            custom_message: 自定义等待消息。如果不提供，将使用默认消息。
        """
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        wait_seconds = self.config.wait_minutes * 60
        
        if elapsed < wait_seconds:
            remaining = wait_seconds - elapsed
            if self.config.show_progress:
                message = custom_message or f"等待 {self.config.wait_minutes} 分钟后继续..."
                with tqdm(
                    total=remaining,
                    desc=message,
                    unit="s",
                    bar_format="{desc} {percentage:3.0f}%|{bar}| {n:.1f}/{total:.1f}s"
                ) as pbar:
                    while remaining > 0:
                        time.sleep(0.1)  # 每0.1秒更新一次进度
                        pbar.update(0.1)
                        remaining -= 0.1
            else:
                time.sleep(remaining)
        
        self.last_call_time = time.time()
    
    def reset_timer(self):
        """重置计时器"""
        self.last_call_time = 0 