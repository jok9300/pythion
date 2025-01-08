"""
模型选择器模块

提供统一的模型选择功能，包括：
- 选择基础模型
- 选择具体的Gemini模型
"""

import tkinter as tk
from tkinter import ttk

class ModelSelector:
    """模型选择器类"""
    
    @staticmethod
    def select_model(models):
        """选择基础模型
        
        Args:
            models: 可用模型列表
            
        Returns:
            str: 选择的模型名称
        """
        root = tk.Tk()
        root.title("选择模型")
        
        # 设置窗口大小和位置
        window_width = 300
        window_height = 250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标题标签
        label = ttk.Label(main_frame, text="请选择要使用的模型：")
        label.pack(pady=(0, 10))
        
        # 创建单选按钮框架
        radio_frame = ttk.Frame(main_frame)
        radio_frame.pack(fill=tk.BOTH, expand=True)
        
        selected_model = tk.StringVar()
        
        # 添加单选按钮
        for model in models:
            ttk.Radiobutton(
                radio_frame,
                text=model.capitalize(),
                variable=selected_model,
                value=model
            ).pack(pady=5)
        
        selected_model.set(models[0])
        
        # 创建底部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 添加确认按钮
        confirm_button = ttk.Button(button_frame, text="确认", command=root.quit)
        confirm_button.pack(pady=5)
        
        root.mainloop()
        result = selected_model.get()
        root.destroy()
        return result
    
    @staticmethod
    def select_gemini_model():
        """选择具体的Gemini模型
        
        Returns:
            str: 选择的Gemini模型名称
        """
        GEMINI_MODELS = [
            "gemini-2.0-flash-exp",
            "gemini-exp-1206",
            "gemini-2.0-flash-thinking-exp-1219",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ]
        
        root = tk.Tk()
        root.title("选择 Gemini 模型")
        
        # 设置窗口大小和位置
        window_width = 400
        window_height = 450
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标题标签
        label = ttk.Label(main_frame, text="请选择要使用的 Gemini 模型：")
        label.pack(pady=(0, 10))
        
        # 创建单选按钮框架
        radio_frame = ttk.Frame(main_frame)
        radio_frame.pack(fill=tk.BOTH, expand=True)
        
        selected_model = tk.StringVar()
        
        # 添加单选按钮
        for model in GEMINI_MODELS:
            ttk.Radiobutton(
                radio_frame,
                text=model,
                variable=selected_model,
                value=model
            ).pack(pady=5)
        
        selected_model.set(GEMINI_MODELS[0])
        
        # 创建底部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 添加确认按钮
        confirm_button = ttk.Button(button_frame, text="确认", command=root.quit)
        confirm_button.pack(pady=5)
        
        root.mainloop()
        result = selected_model.get()
        root.destroy()
        return result 