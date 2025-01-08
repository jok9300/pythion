"""
API工厂模块

提供统一的API调用和文件处理接口
"""

import os
from typing import List, Tuple, Optional
from tkinter import messagebox
from tqdm import tqdm
from base_api import BaseAPI
from gemini_api import GeminiAPI
from kimi_api import KimiAPI
from deepseek_api import DeepSeekAPI
from rate_limiter import RateLimiter
import time

class ArticleAnalyzer:
    """文章分析器类"""
    
    def __init__(self):
        """初始化文章分析器"""
        self.api = None
        self.rate_limiter = None
        
    def create_api(self, model_type: str, **kwargs) -> Optional[BaseAPI]:
        """创建API实例
        
        Args:
            model_type: 模型类型 (gemini/kimi/deepseek)
            **kwargs: 额外的参数，例如具体的模型名称等
            
        Returns:
            BaseAPI: API实例
        """
        if model_type == "gemini":
            self.api = GeminiAPI(**kwargs)
        elif model_type == "kimi":
            self.api = KimiAPI()
        elif model_type == "deepseek":
            self.api = DeepSeekAPI()
        return self.api
    
    def process_single_file(self, file_path: str, prompt_file: str, pbar: Optional[tqdm] = None) -> Tuple[str, str]:
        """处理单个文件
        
        Args:
            file_path: 文件路径
            prompt_file: 提示词文件名
            pbar: tqdm进度条对象
            
        Returns:
            Tuple[str, str]: (标题, 分析结果)
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            # 使用文件名作为标题
            title = os.path.splitext(os.path.basename(file_path))[0]
            
            # 格式化文本并调用API
            max_retries = 3
            retry_count = 0
            
            # 创建API调用进度条
            api_pbar = tqdm(total=100, desc="API调用进度", unit="%", leave=False)
            
            while retry_count < max_retries:
                try:
                    # 更新进度到25%表示开始格式化
                    api_pbar.n = 0
                    api_pbar.set_description("正在格式化文本")
                    api_pbar.update(25)
                    
                    formatted_text = self.api.format_article(text, title, prompt_file)
                    if not formatted_text:
                        if pbar:
                            pbar.write(f"格式化文本失败: {file_path}")
                        api_pbar.close()
                        return None, None
                    
                    # 更新进度到50%表示开始调用API
                    api_pbar.set_description("正在调用API")
                    api_pbar.update(25)
                    
                    result = self.api.call_api(text, formatted_text)
                    
                    # 更新进度到100%表示完成
                    api_pbar.set_description("API调用完成")
                    api_pbar.update(50)
                    
                    if result:
                        api_pbar.close()
                        return title, result
                    
                    if pbar:
                        pbar.write(f"API调用失败: {file_path}")
                    
                except Exception as api_error:
                    error_msg = str(api_error).lower()
                    if pbar:
                        pbar.write(f"API调用出错 (尝试 {retry_count + 1}/{max_retries}): {str(api_error)}")
                    
                    if "blocked prompt" in error_msg:
                        if pbar:
                            pbar.write("提示词被模型拒绝，请检查提示词内容是否合规")
                        api_pbar.close()
                        return None, None
                    elif "response.candidates is empty" in error_msg:
                        if pbar:
                            pbar.write("模型未返回结果，等待后重试...")
                    elif "rate limit" in error_msg:
                        if pbar:
                            pbar.write("触发速率限制，等待后重试...")
                    
                    # 重置进度条
                    api_pbar.n = 0
                    api_pbar.refresh()
                    
                    # 如果不是最后一次重试，等待后继续
                    if retry_count < max_retries - 1:
                        wait_time = (retry_count + 1) * 60  # 递增等待时间
                        if pbar:
                            pbar.write(f"等待 {wait_time} 秒后重试...")
                        api_pbar.set_description(f"等待重试 ({wait_time}秒)")
                        time.sleep(wait_time)
                
                retry_count += 1
            
            if pbar:
                pbar.write(f"达到最大重试次数 ({max_retries})，放弃处理")
            api_pbar.close()
            return None, None
                
        except Exception as e:
            if pbar:
                pbar.write(f"处理文件时发生错误: {e}")
            return None, None
    
    def process_file(self, file_path: str, prompt_file: str, pbar: Optional[tqdm] = None) -> Tuple[bool, Optional[str]]:
        """处理单个文件并保存结果
        
        Args:
            file_path: 文件路径
            prompt_file: 提示词文件名
            pbar: tqdm进度条对象
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 结果文件路径)
        """
        try:
            # 处理文件
            title, result = self.process_single_file(file_path, prompt_file, pbar)
            if not title or not result:
                return False, None
                
            # 格式化为markdown
            md_result = self.api.format_to_md(result)
            
            # 构建保存文件名和目录
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            if isinstance(self.api, GeminiAPI):
                model_version = self.api.model_name.split('-')[1]
                save_name = f"{base_name}_gemini{model_version}.md"
                model_dir = os.path.join("book_2", "Gemini")
            else:
                api_name = self.api.__class__.__name__.replace('API', '')
                save_name = f"{base_name}_{api_name.lower()}.md"
                model_dir = os.path.join("book_2", api_name)
            
            # 确保目录存在
            os.makedirs(model_dir, exist_ok=True)
            save_path = os.path.join(model_dir, save_name)
            
            # 保存结果
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(md_result)
                
            if pbar:
                pbar.write(f"结果已保存到: {save_path}")
            return True, save_path
        except Exception as e:
            if pbar:
                pbar.write(f"处理文件时发生错误: {e}")
            return False, None
    
    def process_files(self, file_paths: List[str], prompt_file: str) -> None:
        """处理多个文件
        
        Args:
            file_paths: 文件路径列表
            prompt_file: 提示词文件路径
        """
        if not self.api:
            print("错误：API未初始化")
            return
            
        # 初始化速率限制器
        if not self.rate_limiter:
            self.rate_limiter = RateLimiter()
        
        # 重置速率限制器的计时器
        self.rate_limiter.reset_timer()
            
        total_files = len(file_paths)
        print(f"\n开始处理 {total_files} 个文件...")
        
        # 收集失败的任务
        failed_tasks = []
        consecutive_failures = 0  # 连续失败计数
        
        # 使用tqdm创建进度条
        with tqdm(total=total_files, desc="处理进度", unit="文件") as pbar:
            for i, file_path in enumerate(file_paths):
                current_file = os.path.basename(file_path)
                
                # 如果不是第一个文件，先等待
                if i > 0:
                    try:
                        pbar.set_description(f"等待处理: {current_file}")
                        self.rate_limiter.wait(f"等待处理: {current_file}")
                    except KeyboardInterrupt:
                        pbar.set_description("用户中断处理")
                        break
                
                pbar.set_description(f"正在处理: {current_file}")
                
                # 处理当前文件
                success, _ = self.process_file(file_path, prompt_file, pbar)
                
                if not success:
                    failed_tasks.append(file_path)
                    consecutive_failures += 1
                    pbar.set_description(f"处理失败: {current_file}")
                    
                    # 如果连续失败超过3次，询问是否继续
                    if consecutive_failures >= 3:
                        if not messagebox.askyesno("连续失败", 
                            "已连续失败3次，是否继续处理？\n选择'否'将暂停处理并进入重试模式"):
                            break
                        consecutive_failures = 0  # 重置计数
                else:
                    consecutive_failures = 0  # 重置连续失败计数
                    pbar.set_description(f"处理成功: {current_file}")
                    # 更新最后调用时间
                    self.rate_limiter.last_call_time = time.time()
                
                # 更新进度条
                pbar.update(1)
        
        print("\n所有文件处理完成!")
        
        # 处理失败的任务
        if failed_tasks:
            print(f"\n有 {len(failed_tasks)} 个任务失败。")
            retry_options = ["立即重试", "延长等待时间后重试", "取消"]
            choice = messagebox.askyesnocancel("重试失败任务", 
                "是否重试失败的任务？\n'是': 立即重试\n'否': 延长等待时间后重试\n'取消': 不重试")
            
            if choice is not None:  # 不是取消
                if not choice:  # 选择延长等待时间
                    self.rate_limiter.update_config(
                        default_minutes=self.rate_limiter.config.wait_minutes * 2)
                self.retry_failed_tasks(failed_tasks, prompt_file)
                
    def retry_failed_tasks(self, failed_tasks: List[str], prompt_file: str) -> None:
        """重试失败的任务
        
        Args:
            failed_tasks: 失败的任务列表
            prompt_file: 提示词文件名
        """
        print("\n开始重试失败的任务...")
        
        # 使用tqdm创建进度条
        with tqdm(total=len(failed_tasks), desc="重试进度", unit="文件") as pbar:
            for i, file_path in enumerate(failed_tasks):
                file_name = os.path.basename(file_path)
                pbar.set_description(f"正在重试: {file_name}")
                
                # 如果不是第一个文件，等待指定时间
                if i > 0:
                    pbar.set_description(f"等待后重试: {file_name}")
                    self.rate_limiter.wait(f"等待重试: {file_name}")
                    
                success, _ = self.process_file(file_path, prompt_file, pbar)
                if success:
                    pbar.set_description(f"重试成功: {file_name}")
                else:
                    pbar.set_description(f"重试失败: {file_name}")
                
                # 更新进度条
                pbar.update(1)
    
    def list_available_models(self) -> List[str]:
        """列出可用的模型
        
        Returns:
            List[str]: 可用模型列表
        """
        return ["gemini", "kimi", "deepseek"] 