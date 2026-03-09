"""
hello_agents.core.message
=========================

消息系统 —— 定义 Agent 内部流转的消息数据结构。

本模块提供:
    - ``MessageRole``: 枚举，表示消息发送方角色（system / user / assistant / tool）
    - ``Message``    : 数据类，承载单条消息的完整信息

消息对象在 Agent 历史记录、LLM 请求构造以及工具调用结果传递中统一使用，
确保整个框架的数据流格式一致。

典型用法::

    from hello_agents.core.message import Message, MessageRole

    msg = Message(role=MessageRole.USER, content="请帮我计算 1+1")
    print(msg.to_dict())
    # {'role': 'user', 'content': '请帮我计算 1+1'}
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class MessageRole(str, enum.Enum):
    """消息发送方角色枚举。

    继承 str 以便直接用于 JSON 序列化与字典构造。
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """单条消息数据类。

    Attributes:
        role (MessageRole): 消息角色。
        content (str): 消息文本内容。
        name (Optional[str]): 可选的发送方名称，用于多 Agent 场景区分身份。
        tool_call_id (Optional[str]): 工具调用 ID，仅 role=TOOL 时有效。
        timestamp (datetime): 消息创建时间戳，自动填充。
    """

    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, str]:
        """将消息序列化为 LLM API 所需的字典格式。

        Returns:
            仅含 ``role`` 与 ``content`` 的字典（符合 OpenAI/Anthropic 格式）。
        """
        return {"role": self.role.value, "content": self.content}

    @classmethod
    def system(cls, content: str) -> "Message":
        """快捷构造 system 消息。"""
        return cls(role=MessageRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        """快捷构造 user 消息。"""
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        """快捷构造 assistant 消息。"""
        return cls(role=MessageRole.ASSISTANT, content=content)
