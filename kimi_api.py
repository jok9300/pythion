"""
Kimi API 模块

提供与 Kimi API 交互的功能
"""

import os
import sys
import requests
import time
from tqdm import tqdm
from base_api import BaseAPI
from api_keys.api_keys import APIKeys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from prompts.analysis_prompts import NovelAnalysisPrompts

class KimiAPI(BaseAPI):
    """Kimi API 封装类"""
    
    # Kimi API 服务端点
    API_ENDPOINT = "https://api.moonshot.cn/v1/chat/completions"
    # 默认使用的模型名称
    DEFAULT_MODEL = "moonshot-v1-auto"

    def __init__(self, api_key=None, temperature=0.7):
        """初始化 Kimi API 客户端"""
        self.api_key = api_key or APIKeys.get_kimi_key()
        self.temperature = max(0.0, min(1.0, temperature))  # 确保在 0-1 范围内
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @classmethod
    def create_default(cls):
        """使用默认 API Key 创建实例"""
        return cls(APIKeys.get_kimi_key())

    def update_api_key(self, new_api_key):
        """更新 API Key"""
        self.api_key = new_api_key
        self.headers["Authorization"] = f"Bearer {self.api_key}"

    def call_api(self, text, prompt, max_retries=3):
        """调用 Kimi API，包含重试机制和错误处理"""
        # 构建系统消息（提示词）
        system_message = {
            "model": self.DEFAULT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # 降低温度以提高稳定性
            "top_p": 0.1,  # 降低随机性，提高输出的确定性
            "presence_penalty": 0.1,  # 降低重复内容的可能性
            "frequency_penalty": 0.1,  # 鼓励使用更多样的词汇
            "stream": False
        }

        # 构建用户消息（待分析文本）
        user_message = {
            "model": self.DEFAULT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,  # 降低温度以提高稳定性
            "top_p": 0.1,  # 降低随机性，提高输出的确定性
            "presence_penalty": 0.1,  # 降低重复内容的可能性
            "frequency_penalty": 0.1,  # 鼓励使用更多样的词汇
            "stream": False
        }

        # 强制等待一段时间，让模型有充足的处理时间
        print("\n正在进行深度思考分析...")
        time.sleep(15)  # 增加到15秒的初始思考时间

        with tqdm(total=max_retries, desc="API调用进度") as pbar:
            for attempt in range(max_retries):
                try:
                    # 首先发送系统消息（提示词）
                    response = requests.post(
                        self.API_ENDPOINT,
                        headers=self.headers,
                        json=system_message,
                        timeout=120  # 增加超时时间到2分钟
                    )
                    response.raise_for_status()
                    
                    # 等待系统消息处理
                    print("\n正在处理系统提示...")
                    time.sleep(10)  # 增加系统消息处理时间

                    # 然后发送用户消息（待分析文本）
                    response = requests.post(
                        self.API_ENDPOINT,
                        headers=self.headers,
                        json=user_message,
                        timeout=120  # 增加超时时间到2分钟
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # 每次调用后进行充分的思考时间
                    print("\n正在整理分析结果...")
                    time.sleep(10)  # 增加到10秒的后处理时间
                    
                    pbar.update(max_retries - attempt)
                    return result["choices"][0]["message"]["content"]
                except requests.exceptions.RequestException as e:
                    print(f"\n尝试 {attempt+1}/{max_retries}：Kimi 服务请求失败 ({e})。等待并重试...")
                    time.sleep(10 + 5 ** attempt)  # 增加重试等待时间
                    pbar.update(1)
                except Exception as e:
                    print(f"\n调用 Kimi API 时发生其他错误：{e}")
                    pbar.update(max_retries - attempt)
                    return None
        print(f"\n所有尝试均失败，Kimi 服务不可用.")
        return None

    def format_article(self, text: str, title: str, prompt_file: str) -> str:
        """格式化文章内容，添加标题信息"""
        return NovelAnalysisPrompts.get_prompt(title, text, prompt_file)

    def format_to_md(self, analysis_result):
        """格式化分析结果为 Markdown 格式"""
        return NovelAnalysisPrompts.format_to_markdown(analysis_result) 