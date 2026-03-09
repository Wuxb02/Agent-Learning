"""
hello_agents.agents.reflection_agent
======================================

ReflectionAgent —— 带自我反思与输出修订能力的 Agent 实现。

ReflectionAgent 采用"生成 → 反思 → 修订"三阶段范式：
    1. **生成 (Generate)** : 基于用户输入产生初稿回复。
    2. **反思 (Reflect)**  : 对初稿进行批判性评估，指出问题与改进方向。
    3. **修订 (Revise)**   : 根据反思结果生成改进版本。

反思循环可执行多轮（由 ``reflection_rounds`` 控制）。

参考论文: *Reflexion: Language Agents with Verbal Reinforcement Learning*
          (Shinn et al., 2023)

典型用法::

    agent = ReflectionAgent(
        name="reflect",
        llm=llm,
        reflection_rounds=2,
    )
    answer = agent.run("写一篇关于气候变化的摘要")
"""

from __future__ import annotations

from typing import Optional

from hello_agents.core.agent import Agent
from hello_agents.core.config import Config
from hello_agents.core.llm import HelloAgentsLLM
from hello_agents.core.message import Message, MessageRole


class ReflectionAgent(Agent):
    """带自我反思与迭代修订能力的 Agent。

    Attributes:
        reflection_rounds (int): 反思-修订的循环轮数。
        generate_prompt (str): 初始生成阶段的系统提示词。
        reflect_prompt (str): 反思阶段的系统提示词。
        revise_prompt (str): 修订阶段的系统提示词。
    """

    _DEFAULT_GENERATE = "你是一个专业助手，请根据用户的要求生成高质量的回复。"
    _DEFAULT_REFLECT = (
        "你是一个严格的评审员。请对以下回复进行批判性分析，"
        "指出逻辑漏洞、事实错误、表达不清或遗漏的要点，并给出具体的改进建议。"
    )
    _DEFAULT_REVISE = (
        "你是一个专业助手。请根据以下评审意见，对原回复进行修订和改进，"
        "输出最终的优化版本。"
    )

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        reflection_rounds: int = 1,
        generate_prompt: Optional[str] = None,
        reflect_prompt: Optional[str] = None,
        revise_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> None:
        """初始化 ReflectionAgent。

        Args:
            name: Agent 名称。
            llm: LLM 接口对象。
            reflection_rounds: 反思-修订循环轮数，默认为 1。
            generate_prompt: 覆盖默认的生成阶段系统提示词。
            reflect_prompt: 覆盖默认的反思阶段系统提示词。
            revise_prompt: 覆盖默认的修订阶段系统提示词。
            config: 可选配置对象。
        """
        super().__init__(name=name, llm=llm, config=config)
        self.reflection_rounds = reflection_rounds
        self.generate_prompt = generate_prompt or self._DEFAULT_GENERATE
        self.reflect_prompt = reflect_prompt or self._DEFAULT_REFLECT
        self.revise_prompt = revise_prompt or self._DEFAULT_REVISE

    def run(self, user_input: str) -> str:
        """执行生成-反思-修订流程。

        Args:
            user_input: 用户输入的任务描述或问题。

        Returns:
            经过反思修订后的最终回复文本。
        """
        # 阶段一：生成初稿
        draft = self.llm.chat([
            Message.system(self.generate_prompt).to_dict(),
            {"role": "user", "content": user_input},
        ])

        # 阶段二 & 三：多轮反思与修订
        current = draft
        for _ in range(self.reflection_rounds):
            # 反思
            critique = self.llm.chat([
                Message.system(self.reflect_prompt).to_dict(),
                {"role": "user", "content": f"原始任务：{user_input}\n\n当前回复：\n{current}"},
            ])

            # 修订
            current = self.llm.chat([
                Message.system(self.revise_prompt).to_dict(),
                {
                    "role": "user",
                    "content": (
                        f"原始任务：{user_input}\n\n"
                        f"当前回复：\n{current}\n\n"
                        f"评审意见：\n{critique}"
                    ),
                },
            ])

        self.add_message(MessageRole.USER, user_input)
        self.add_message(MessageRole.ASSISTANT, current)
        return current
