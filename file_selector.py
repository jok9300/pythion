"""
文件选择器模块

提供统一的文件选择功能，包括：
- 选择输入文件
- 选择提示词文件
- 选择保存位置
"""

import os
import tkinter as tk
from tkinter import filedialog

class FileSelector:
    """文件选择器类"""
    
    @staticmethod
    def select_input_files(title="选择要分析的文件"):
        """选择输入文件，支持多选
        
        Args:
            title: 对话框标题
            
        Returns:
            tuple: 选择的文件路径列表
        """
        root = tk.Tk()
        root.withdraw()
        initial_dir = os.path.join(os.getcwd(), "book_1")
        file_paths = filedialog.askopenfilenames(
            title=title,
            initialdir=initial_dir,
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        return file_paths
    
    @staticmethod
    def select_prompt_file(title="选择提示词文件"):
        """选择提示词文件
        
        Args:
            title: 对话框标题
            
        Returns:
            str: 选择的文件路径
        """
        root = tk.Tk()
        root.withdraw()
        initial_dir = os.path.join(os.getcwd(), "prompts")
        file_path = filedialog.askopenfilename(
            title=title,
            initialdir=initial_dir,
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            # 返回相对于prompts目录的路径
            return os.path.relpath(file_path, os.path.join(os.getcwd(), "prompts"))
        return None
    
    @staticmethod
    def select_save_file(title="选择保存位置", default_filename=None, model_name=None):
        """选择保存文件位置
        
        Args:
            title: 对话框标题
            default_filename: 默认文件名
            model_name: 模型名称，用于确定保存目录
            
        Returns:
            str: 选择的保存路径
        """
        root = tk.Tk()
        root.withdraw()
        
        initial_file = default_filename if default_filename else ""
        
        # 根据模型名称确定保存目录
        base_dir = os.path.join(os.getcwd(), "book_2")
        if model_name:
            # 将模型名称首字母大写
            model_dir = model_name.capitalize()
            initial_dir = os.path.join(base_dir, model_dir)
        else:
            initial_dir = base_dir
            
        # 确保目录存在
        os.makedirs(initial_dir, exist_ok=True)
        
        file_path = filedialog.asksaveasfilename(
            title=title,
            defaultextension=".md",
            initialfile=initial_file,
            initialdir=initial_dir,
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        return file_path
    
    @staticmethod
    def select_save_directory(title="选择保存目录"):
        """选择保存目录
        
        Args:
            title: 对话框标题
            
        Returns:
            str: 选择的目录路径，如果用户取消则返回 None
        """
        root = tk.Tk()
        root.withdraw()
        
        # 默认打开 book_2 目录
        initial_dir = os.path.join(os.getcwd(), "book_2")
        os.makedirs(initial_dir, exist_ok=True)
        
        directory = filedialog.askdirectory(
            title=title,
            initialdir=initial_dir
        )
        
        return directory if directory else None 