"""
hello_agents.core.config
========================

配置管理模块 —— 集中管理 HelloAgents 框架的所有运行时参数。

``Config`` 使用 dataclass 实现，支持：
    1. 直接实例化并传入关键字参数。
    2. 通过 :meth:`Config.from_env` 从环境变量加载（适合生产环境）。
    3. 通过 :meth:`Config.from_dict` 从字典加载（适合配置文件场景）。

环境变量对照表:
    HA_PROVIDER      —— LLM 提供商，默认 ``anthropic``
    HA_MODEL         —— 模型名称，默认 ``claude-sonnet-4-6``
    HA_API_KEY       —— API 密钥
    HA_MAX_TOKENS    —— 单次最大 token 数，默认 ``4096``
    HA_TEMPERATURE   —— 采样温度，默认 ``0.7``
    HA_MAX_STEPS     —— Agent 最大推理步数，默认 ``10``

典型用法::

    import os
    os.environ["HA_API_KEY"] = "sk-ant-..."

    from hello_agents.core.config import Config
    cfg = Config.from_env()
"""

from __future__ import annotations

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel

class Config(BaseModel):
    """HelloAgents配置类"""
    
    # LLM配置
    default_model: str = "gpt-3.5-turbo"
    default_provider: str = "openai"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    # 系统配置
    debug: bool = False
    log_level: str = "INFO"
    
    # 其他配置
    max_history_length: int = 100
    
    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置"""
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS")) if os.getenv("MAX_TOKENS") else None,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.dict()