from colorama import Fore
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.utils import print_text_animated
from dotenv import load_dotenv
import os

load_dotenv()
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL_ID")

model = ModelFactory.create(
    model_platform=ModelPlatformType.QWEN,
    model_type=LLM_MODEL,
    url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)

task_prompt = """
创作一本关于"拖延症心理学"的短文，目标读者是对心理学感兴趣的普通大众。
要求：
1. 内容科学严谨，基于实证研究
2. 语言通俗易懂，避免过多专业术语
3. 包含实用的改善建议和案例分析
4. 篇幅控制在1000-2000字
5. 结构清晰，包含引言、核心章节和总结
"""

print(Fore.YELLOW + f"协作任务:\n{task_prompt}\n")

# --- 初始化三个 Agent ---
writer = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="作家",
        content=(
            "你是一位专业作家，擅长将复杂知识转化为通俗易懂的文章。"
            "你负责规划文章结构、整合专家建议并完成文章写作。"
        ),
    ),
    model=model,
)

psychologist = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="心理学家",
        content=(
            "你是一位专业心理学家，拥有丰富的拖延症研究经验。"
            "你负责提供科学严谨的实证研究数据、理论依据和专业见解。"
        ),
    ),
    model=model,
)

proofreader = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="校对",
        content=(
            "你是一位专业文字校对编辑，擅长逻辑梳理和语言润色。"
            "你负责检查文章的连贯性、准确性与可读性，并提出具体修改建议。"
        ),
    ),
    model=model,
)

print(Fore.CYAN + "=== 开始三方协作创作 ===\n")

# --- 第一轮：作家规划文章结构 ---
writer_resp = writer.step(
    BaseMessage.make_user_message(
        role_name="协调者",
        content=f"请根据以下任务，规划文章的整体结构和各章节写作要点：\n{task_prompt}",
    )
)
print_text_animated(Fore.BLUE + f"【作家 · 结构规划】\n\n{writer_resp.msg.content}\n")

# --- 第二轮：心理学家提供专业内容 ---
psychologist_resp = psychologist.step(
    BaseMessage.make_user_message(
        role_name="协调者",
        content=(
            f"作家规划了以下文章结构：\n{writer_resp.msg.content}\n\n"
            "请针对每个章节，提供详细的心理学研究支撑、经典案例和实用建议。"
        ),
    )
)
print_text_animated(
    Fore.GREEN + f"【心理学家 · 专业内容】\n\n{psychologist_resp.msg.content}\n"
)

# --- 第三轮：作家撰写完整草稿 ---
draft_resp = writer.step(
    BaseMessage.make_user_message(
        role_name="协调者",
        content=(
            "请结合你的结构规划和心理学家的专业内容，撰写完整的文章草稿：\n\n"
            f"心理学家的内容：\n{psychologist_resp.msg.content}"
        ),
    )
)
print_text_animated(Fore.BLUE + f"【作家 · 文章草稿】\n\n{draft_resp.msg.content}\n")

# --- 第四轮：校对审阅草稿 ---
proofreader_resp = proofreader.step(
    BaseMessage.make_user_message(
        role_name="协调者",
        content=(
            "请对以下文章草稿进行全面校对，"
            "重点检查逻辑连贯性、语言流畅度、事实准确性，并列出具体修改建议：\n\n"
            f"{draft_resp.msg.content}"
        ),
    )
)
print_text_animated(
    Fore.MAGENTA + f"【校对 · 审阅意见】\n\n{proofreader_resp.msg.content}\n"
)

# --- 第五轮：作家根据校对意见完成终稿 ---
final_resp = writer.step(
    BaseMessage.make_user_message(
        role_name="协调者",
        content=(
            "请根据校对的修改建议，完成文章的最终版本：\n\n"
            f"校对意见：\n{proofreader_resp.msg.content}"
        ),
    )
)
print_text_animated(Fore.BLUE + f"【作家 · 最终版本】\n\n{final_resp.msg.content}\n")

print(Fore.YELLOW + "✅ 三方协作创作完成！")
