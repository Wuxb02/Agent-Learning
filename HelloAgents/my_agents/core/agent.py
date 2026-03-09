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

from abc import ABC
from typing import Optional

from my_agents.core.config import Config
from my_agents.core.llm import HelloAgentsLLM
from my_agents.core.message import Message, MessageRole



class Agent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: list[Message] = []
    
    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent"""
        pass
    
    def add_message(self, message: Message):
        """添加消息到历史记录"""
        self._history.append(message)
    
    def clear_history(self):
        """清空历史记录"""
        self._history.clear()
    
    def get_history(self) -> list[Message]:
        """获取历史记录"""
        return self._history.copy()
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider})"
