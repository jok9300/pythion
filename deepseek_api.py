"""
DeepSeek API 模块

提供与 DeepSeek API 交互的功能
"""

import os
import sys
import time
from tqdm import tqdm
from openai import OpenAI
from base_api import BaseAPI
from api_keys.api_keys import APIKeys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from prompts.analysis_prompts import NovelAnalysisPrompts

class DeepSeekAPI(BaseAPI):
    """DeepSeek API 封装类"""
    
    # DeepSeek API 服务端点
    BASE_URL = "https://api.deepseek.com"
    # 默认使用的模型名称
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self, api_key=None, temperature=0.7):
        """初始化 DeepSeek API 客户端"""
        self.api_key = api_key or APIKeys.get_deepseek_key()
        self.temperature = max(0.0, min(1.0, temperature))  # 确保在 0-1 范围内
        self.client = OpenAI(api_key=self.api_key, base_url=self.BASE_URL)

    @classmethod
    def create_default(cls):
        """使用默认 API Key 创建实例"""
        return cls(APIKeys.get_deepseek_key())

    def update_api_key(self, new_api_key):
        """更新 API Key"""
        self.api_key = new_api_key
        self.client = OpenAI(api_key=self.api_key, base_url=self.BASE_URL)

    def call_api(self, text, prompt, max_retries=3):
        """调用 DeepSeek API，包含重试机制和错误处理"""
        # 构建消息列表
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]

        # 强制等待一段时间，让模型有充足的处理时间
        print("\n正在进行深度思考分析...")
        time.sleep(15)  # 增加到15秒的初始思考时间

        with tqdm(total=max_retries, desc="API调用进度") as pbar:
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.DEFAULT_MODEL,
                        messages=messages,
                        temperature=0.3,  # 降低温度以提高稳定性
                        top_p=0.1,  # 降低随机性，提高输出的确定性
                        presence_penalty=0.1,  # 降低重复内容的可能性
                        frequency_penalty=0.1,  # 鼓励使用更多样的词汇
                        max_tokens=4096,  # 增加最大输出长度
                        n=1,  # 每次只生成一个最优结果
                        stream=False
                    )
                    
                    # 每次调用后进行充分的思考时间
                    print("\n正在整理分析结果...")
                    time.sleep(10)  # 增加到10秒的后处理时间
                    
                    pbar.update(max_retries - attempt)
                    return response.choices[0].message.content
                except Exception as e:
                    print(f"\n尝试 {attempt+1}/{max_retries}：DeepSeek 服务请求失败 ({e})。等待并重试...")
                    time.sleep(10 + 5 ** attempt)  # 增加重试等待时间
                    pbar.update(1)
            print(f"\n所有尝试均失败，DeepSeek 服务不可用.")
            return None

    def format_article(self, text: str, title: str, prompt_file: str) -> str:
        """格式化文章内容，添加标题信息"""
        return NovelAnalysisPrompts.get_prompt(title, text, prompt_file)

    def format_to_md(self, analysis_result):
        """格式化分析结果为 Markdown 格式"""
        return NovelAnalysisPrompts.format_to_markdown(analysis_result) 