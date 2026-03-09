"""
hello_agents.core.agent
=======================

定义 Agent 抽象基类（Abstract Base Class）。

所有具体 Agent（SimpleAgent、ReActAgent 等）均继承本模块中的 ``Agent``。
子类必须实现 ``run`` 方法，该方法接收用户输入并返回最终回复。

典型用法::

    from hello_agents.core.agent import Agent

    class MyAgent(Agent):
        def run(self, user_input: str) -> str:
            ...
"""

from __future__ import annotations

import abc
from typing import Optional

from hello_agents.core.config import Config
from hello_agents.core.llm import HelloAgentsLLM
from hello_agents.core.message import Message, MessageRole


class Agent(abc.ABC):
    """Agent 抽象基类。

    所有具体 Agent 实现必须继承此类并实现 :meth:`run` 方法。

    Attributes:
        name (str): Agent 的唯一名称，用于日志与追踪。
        llm (HelloAgentsLLM): 底层语言模型接口。
        config (Config): 运行时配置对象。
        _history (list[Message]): 对话历史记录。
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        config: Optional[Config] = None,
    ) -> None:
        """初始化 Agent。

        Args:
            name: Agent 名称。
            llm: 已实例化的 LLM 接口对象。
            config: 可选的配置对象；若为 None 则使用默认配置。
        """
        self.name = name
        self.llm = llm
        self.config = config or Config()
        self._history: list[Message] = []

    @abc.abstractmethod
    def run(self, user_input: str) -> str:
        """执行 Agent 主循环，处理用户输入并返回回复。

        Args:
            user_input: 来自用户的原始输入文本。

        Returns:
            Agent 生成的最终回复字符串。

        Raises:
            HelloAgentsError: 当推理过程中发生框架级别错误时抛出。
        """

    def reset(self) -> None:
        """清空对话历史，使 Agent 回到初始状态。"""
        self._history.clear()

    def add_message(self, role: MessageRole, content: str) -> None:
        """向对话历史中追加一条消息。

        Args:
            role: 消息角色（用户、助手或系统）。
            content: 消息文本内容。
        """
        self._history.append(Message(role=role, content=content))

    @property
    def history(self) -> list[Message]:
        """返回当前对话历史的只读副本。"""
        return list(self._history)
