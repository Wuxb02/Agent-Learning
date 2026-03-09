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

from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel


MessageRole = Literal["user", "assistant", "system", "tool"]

class Message(BaseModel):
    """消息类"""
    
    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, content: str, role: MessageRole, **kwargs):
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get('timestamp', datetime.now()),
            metadata=kwargs.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（OpenAI API格式）"""
        return {
            "role": self.role,
            "content": self.content
        }
    
    def __str__(self) -> str:
        return f"[{self.role}] {self.content}"