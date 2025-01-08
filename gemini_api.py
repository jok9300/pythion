"""
Gemini API 模块

提供与 Gemini API 交互的功能
"""

import os
import sys
import google.generativeai as genai
import google.api_core.exceptions
import time
from tqdm import tqdm
from base_api import BaseAPI
from api_keys.api_keys import APIKeys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from prompts.analysis_prompts import NovelAnalysisPrompts

class GeminiAPI(BaseAPI):
    """Gemini API 封装类"""
    
    # 默认使用的模型名称
    DEFAULT_MODEL = "gemini-2.0-flash-exp"

    def __init__(self, api_key=None, model_name=None, temperature=0.7):
        """初始化 Gemini API 客户端
        
        Args:
            api_key (str, optional): API密钥。如果不提供，将使用默认密钥。
            model_name (str, optional): 模型名称。如果不提供，将使用默认模型。
            temperature (float, optional): 生成文本的随机性。范围 0-1，默认 0.7。
        """
        self.api_key = api_key or APIKeys.get_gemini_key()
        self.model_name = model_name or self.DEFAULT_MODEL
        self.temperature = max(0.0, min(1.0, temperature))  # 确保在 0-1 范围内
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    @classmethod
    def create_default(cls, model_name=None):
        """使用默认 API Key 创建实例"""
        return cls(APIKeys.get_gemini_key(), model_name)

    def update_api_key(self, new_api_key):
        """更新 API Key"""
        self.api_key = new_api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def call_api(self, text, prompt, max_retries=3):
        """调用 Gemini API，包含重试机制和错误处理"""
        prompt_with_text = f"{prompt}\n\n{text}"

        # 强制等待一段时间，让模型有充足的处理时间
        print("\n正在进行深度思考分析...")
        time.sleep(15)  # 增加到15秒的初始思考时间

        with tqdm(total=max_retries, desc="API调用进度") as pbar:
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        prompt_with_text,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,  # 降低温度以提高稳定性
                            top_p=0.1,  # 降低随机性，提高输出的确定性
                            top_k=10,   # 减少选择范围，提高质量
                            max_output_tokens=4096,  # 增加最大输出长度
                            candidate_count=1,  # 每次只生成一个最优结果
                        )
                    )
                    
                    # 每次调用后进行充分的思考时间
                    print("\n正在整理分析结果...")
                    time.sleep(10)  # 增加到10秒的后处理时间
                    
                    pbar.update(max_retries - attempt)
                    return response.text
                except google.api_core.exceptions.ServiceUnavailable as e:
                    print(f"\n尝试 {attempt+1}/{max_retries}：Gemini 服务不可用 ({e})。等待并重试...")
                    time.sleep(10 + 5 ** attempt)  # 增加重试等待时间
                    pbar.update(1)
                except Exception as e:
                    print(f"\n调用 Gemini API 时发生其他错误：{e}")
                    pbar.update(max_retries - attempt)
                    return None
        print(f"\n所有尝试均失败，Gemini 服务不可用.")
        return None

    def format_article(self, text: str, title: str, prompt_file: str) -> str:
        """格式化文章内容，添加标题信息"""
        return NovelAnalysisPrompts.get_prompt(title, text, prompt_file)

    def format_to_md(self, analysis_result):
        """格式化分析结果为 Markdown 格式"""
        return NovelAnalysisPrompts.format_to_markdown(analysis_result) 