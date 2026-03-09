"""
hello_agents.agents.simple_agent
=================================

SimpleAgent —— 最简单的对话型 Agent 实现。

SimpleAgent 不涉及工具调用或复杂推理循环，适合以下场景：
    - 单轮问答
    - 多轮上下文对话
    - 快速原型验证

执行流程::

    用户输入 → 拼接历史 → 调用 LLM → 追加历史 → 返回回复

典型用法::

    from hello_agents.core.config import Config
    from hello_agents.core.llm import HelloAgentsLLM
    from hello_agents.agents.simple_agent import SimpleAgent

    cfg = Config.from_env()
    llm = HelloAgentsLLM(cfg)
    agent = SimpleAgent(name="simple", llm=llm, system_prompt="你是一个助手。")

    reply = agent.run("你好，介绍一下自己")
    print(reply)
"""

from __future__ import annotations

from typing import Optional

from hello_agents.core.agent import Agent
from hello_agents.core.config import Config
from hello_agents.core.llm import HelloAgentsLLM
from hello_agents.core.message import Message, MessageRole


class SimpleAgent(Agent):
    """单轮/多轮对话型 Agent，不包含工具调用或推理循环。

    Attributes:
        system_prompt (str): 系统提示词，在每次请求时置于消息列表首位。
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: str = "You are a helpful assistant.",
        config: Optional[Config] = None,
    ) -> None:
        """初始化 SimpleAgent。

        Args:
            name: Agent 名称。
            llm: LLM 接口对象。
            system_prompt: 系统提示词，定义 Agent 的角色与行为。
            config: 可选配置对象。
        """
        super().__init__(name=name, llm=llm, config=config)
        self.system_prompt = system_prompt

    def run(self, user_input: str) -> str:
        """执行单次对话。

        将系统提示、历史消息与当前用户输入拼接后调用 LLM，
        并将新的用户消息和助手回复追加到对话历史中。

        Args:
            user_input: 用户输入文本。

        Returns:
            LLM 生成的回复文本。
        """
        self.add_message(MessageRole.USER, user_input)

        messages = [
            Message.system(self.system_prompt).to_dict(),
            *[m.to_dict() for m in self._history],
        ]

        reply = self.llm.chat(messages)
        self.add_message(MessageRole.ASSISTANT, reply)
        return reply
