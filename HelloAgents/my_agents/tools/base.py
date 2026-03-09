"""
hello_agents.tools.base
========================

工具抽象基类（BaseTool）定义模块。

所有内置工具与用户自定义工具均须继承 ``BaseTool``，并实现：
    - ``name``        : 属性，工具唯一名称（用于注册与 Agent 调用）
    - ``description`` : 属性，供 LLM 理解工具用途的自然语言描述
    - ``run``         : 方法，接收字符串输入并返回字符串结果

工具签名约定::

    工具的 run 方法接受单一字符串 ``tool_input``，
    具体格式由各工具自行定义（如 JSON、逗号分隔等），
    并在 description 中向 Agent 说明。

典型用法::

    from hello_agents.tools.base import BaseTool

    class MyTool(BaseTool):
        name = "my_tool"
        description = "这是一个示例工具，返回输入的大写形式。"

        def run(self, tool_input: str) -> str:
            return tool_input.upper()
"""

from __future__ import annotations

import abc


class BaseTool(abc.ABC):
    """工具抽象基类。

    所有工具必须继承此类并实现 ``name``、``description`` 与 ``run``。

    Attributes:
        name (str): 工具唯一标识符，Agent 通过此名称调用工具。
        description (str): 工具功能的自然语言描述，供 LLM Prompt 使用。
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """工具的唯一名称。"""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """工具功能描述，供 LLM 决策是否使用本工具。"""

    @abc.abstractmethod
    def run(self, tool_input: str) -> str:
        """执行工具逻辑。

        Args:
            tool_input: 传入工具的原始字符串参数，格式由各工具自行定义。

        Returns:
            工具执行结果的字符串表示。

        Raises:
            ToolExecutionError: 当工具内部发生预期外错误时，由上层捕获并包装。
        """

    def __repr__(self) -> str:
        return f"<Tool name={self.name!r}>"
