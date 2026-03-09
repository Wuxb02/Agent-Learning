"""
hello_agents.core.exceptions
=============================

HelloAgents 框架异常体系。

异常继承层级::

    HelloAgentsError            ← 框架根异常（所有框架异常的基类）
    ├── LLMError                ← LLM 调用相关错误
    ├── ToolError               ← 工具执行相关错误
    │   ├── ToolNotFoundError   ← 工具未注册
    │   └── ToolExecutionError  ← 工具运行时错误
    ├── AgentError              ← Agent 推理相关错误
    │   └── MaxStepsExceeded    ← 超出最大推理步数
    └── ConfigError             ← 配置错误

建议：在框架外部捕获 ``HelloAgentsError`` 以统一处理所有框架异常；
在框架内部捕获具体子类以实现精细化错误处理。
"""


class HelloAgentsError(Exception):
    """HelloAgents 框架根异常。

    所有由框架主动抛出的异常均继承自此类，方便外部统一捕获。
    """


# ── LLM 相关 ─────────────────────────────────────────────────────────────────

class LLMError(HelloAgentsError):
    """LLM 调用过程中发生的错误。

    包括：SDK 未安装、网络超时、API 鉴权失败、响应解析异常等。
    """


# ── 工具相关 ──────────────────────────────────────────────────────────────────

class ToolError(HelloAgentsError):
    """工具系统相关错误的基类。"""


class ToolNotFoundError(ToolError):
    """请求的工具名称未在 ToolRegistry 中注册时抛出。"""


class ToolExecutionError(ToolError):
    """工具在执行过程中抛出未预期异常时抛出。

    Attributes:
        tool_name (str): 发生错误的工具名称。
        original (Exception): 原始异常对象。
    """

    def __init__(self, tool_name: str, original: Exception) -> None:
        self.tool_name = tool_name
        self.original = original
        super().__init__(
            f"工具 '{tool_name}' 执行失败: {original}"
        )


# ── Agent 相关 ────────────────────────────────────────────────────────────────

class AgentError(HelloAgentsError):
    """Agent 推理过程中发生的错误的基类。"""


class MaxStepsExceeded(AgentError):
    """Agent 超出配置的最大推理步数（Config.max_steps）时抛出。"""


# ── 配置相关 ──────────────────────────────────────────────────────────────────

class ConfigError(HelloAgentsError):
    """配置项缺失或格式错误时抛出。"""
