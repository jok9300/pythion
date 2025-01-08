"""
Gemini分析器主程序

使用独立模块处理文件选择、API调用和速率限制
"""

from model_selector import ModelSelector
from file_selector import FileSelector
from api_factory import ArticleAnalyzer

def main():
    """主程序入口"""
    analyzer = ArticleAnalyzer()
    file_selector = FileSelector()
    model_selector = ModelSelector()
    
    # 让用户选择模型和文件
    model_name = model_selector.select_model(analyzer.list_available_models())
    if not model_name:
        return
        
    # 如果是Gemini模型，选择具体版本
    if model_name == "gemini":
        gemini_model = model_selector.select_gemini_model()
        if not gemini_model:
            return
        analyzer.create_api(model_name, model_name=gemini_model)
    else:
        analyzer.create_api(model_name)
        
    # 选择输入文件和提示词
    file_paths = file_selector.select_input_files()
    if not file_paths:
        return
        
    prompt_file = file_selector.select_prompt_file()
    if not prompt_file:
        return
        
    # 处理文件
    analyzer.process_files(file_paths, prompt_file)

if __name__ == "__main__":
    main()