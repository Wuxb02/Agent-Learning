import os

from jinja2 import Environment, FileSystemLoader

import main


# 设置模板环境（指定模板文件所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "../../../config/prompts")))


def get_prompt(template_name: str, context: dict) -> str:
    """
    获取并渲染指定的提示词模板。

    参数:
    - template_name (str): 模板文件的名称 (例如 "ReAct.j2")。
    - context (dict): 用于渲染模板的上下文数据。

    返回:
    - str: 渲染后的提示词文本。
    """
    try:
        template = env.get_template(template_name) # 读取prompt
        prompt = template.render(context)
        return prompt
    except Exception as e:
        print(f"错误: 无法加载或渲染模板 '{template_name}'。详情: {e}")
        return ""
    



if __name__ == '__main__':
    print(get_prompt("ReAct.j2", {
                    "tools": '1',
                    "question": 'question',
                    "history": 'history'
                }))
