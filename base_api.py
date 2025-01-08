from abc import ABC, abstractmethod

class BaseAPI(ABC):
    @abstractmethod
    def __init__(self, api_key=None):
        """初始化 API 客户端"""
        pass

    @classmethod
    @abstractmethod
    def create_default(cls):
        """使用默认 API Key 创建实例"""
        pass

    @abstractmethod
    def update_api_key(self, new_api_key):
        """更新 API Key"""
        pass

    @abstractmethod
    def call_api(self, text, prompt, max_retries=3):
        """调用 API"""
        pass

    @abstractmethod
    def format_article(self, text, title):
        """格式化文章内容"""
        pass

    @abstractmethod
    def format_to_md(self, analysis_result):
        """格式化分析结果为 Markdown"""
        pass 