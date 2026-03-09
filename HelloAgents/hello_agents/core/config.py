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
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Config:
    """HelloAgents 框架全局配置。

    Attributes:
        provider (str): LLM 后端提供商标识符。
        model (str): 使用的模型名称。
        api_key (str): API 访问密钥。
        max_tokens (int): 单次 LLM 调用允许生成的最大 token 数。
        temperature (float): 生成温度，控制输出随机性（0~1）。
        max_steps (int): Agent 推理循环的最大步数，防止无限循环。
        extra (dict): 扩展配置字典，供子模块存放自定义参数。
    """

    provider: str = "anthropic"
    model: str = "claude-sonnet-4-6"
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    max_steps: int = 10
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量读取配置并返回 Config 实例。

        Returns:
            以环境变量为基础、缺失项回退到默认值的 Config 对象。
        """
        return cls(
            provider=os.getenv("HA_PROVIDER", "anthropic"),
            model=os.getenv("HA_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("HA_API_KEY", ""),
            max_tokens=int(os.getenv("HA_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("HA_TEMPERATURE", "0.7")),
            max_steps=int(os.getenv("HA_MAX_STEPS", "10")),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """从字典加载配置。

        Args:
            data: 包含配置键值对的字典，未提供的键使用默认值。

        Returns:
            Config 实例。
        """
        known_fields = {
            "provider", "model", "api_key",
            "max_tokens", "temperature", "max_steps",
        }
        init_kwargs = {k: v for k, v in data.items() if k in known_fields}
        extra = {k: v for k, v in data.items() if k not in known_fields}
        return cls(**init_kwargs, extra=extra)
