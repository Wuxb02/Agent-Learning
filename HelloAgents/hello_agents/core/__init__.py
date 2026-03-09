"""
hello_agents.core
=================

核心框架层，定义 HelloAgents 所有基础抽象与公共设施。

导出:
    Agent           —— Agent 抽象基类
    HelloAgentsLLM  —— 统一 LLM 调用接口
    Message         —— 消息数据结构
    MessageRole     —— 消息角色枚举
    Config          —— 全局配置管理器
    HelloAgentsError —— 框架根异常
"""

from hello_agents.core.agent import Agent
from hello_agents.core.llm import HelloAgentsLLM
from hello_agents.core.message import Message, MessageRole
from hello_agents.core.config import Config
from hello_agents.core.exceptions import HelloAgentsError

__all__ = [
    "Agent",
    "HelloAgentsLLM",
    "Message",
    "MessageRole",
    "Config",
    "HelloAgentsError",
]
