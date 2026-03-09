"""
hello_agents.tools.registry
============================

工具注册机制（ToolRegistry）模块。

ToolRegistry 维护一个名称到工具对象的映射表，提供：
    - ``register``  : 注册单个工具
    - ``get``       : 按名称查找工具（不存在时抛出 ToolNotFoundError）
    - ``list_tools``: 列出所有已注册工具的名称与描述
    - ``tool``      : 装饰器，用于以装饰器方式注册函数型工具

典型用法::

    from hello_agents.tools.registry import ToolRegistry
    from hello_agents.tools.builtin.calculator import CalculatorTool

    registry = ToolRegistry()
    registry.register(CalculatorTool())

    tool = registry.get("calculator")
    result = tool.run("1 + 1")

    # 或使用装饰器注册
    @registry.tool(name="echo", description="原样返回输入内容")
    def echo_tool(tool_input: str) -> str:
        return tool_input
"""

from __future__ import annotations

from typing import Callable

from hello_agents.tools.base import BaseTool
from hello_agents.core.exceptions import ToolNotFoundError


class ToolRegistry:
    """工具注册表，管理工具的注册与查找。

    Attributes:
        _tools (dict[str, BaseTool]): 内部映射，key 为工具名称。
    """

    def __init__(self) -> None:
        """初始化空注册表。"""
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册一个工具实例。

        若工具名称已存在则覆盖（更新）旧注册。

        Args:
            tool: 继承自 BaseTool 的工具实例。
        """
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """按名称获取工具。

        Args:
            name: 工具的唯一名称。

        Returns:
            对应的 BaseTool 实例。

        Raises:
            ToolNotFoundError: 若工具名称未注册则抛出。
        """
        if name not in self._tools:
            available = ", ".join(self._tools.keys()) or "（无）"
            raise ToolNotFoundError(
                f"工具 '{name}' 未注册。当前可用工具: {available}"
            )
        return self._tools[name]

    def list_tools(self) -> list[dict[str, str]]:
        """列出所有已注册工具的摘要信息。

        Returns:
            字典列表，每条包含 ``name`` 与 ``description`` 字段。
        """
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools.values()
        ]

    def tool(
        self,
        name: str,
        description: str,
    ) -> Callable[[Callable[[str], str]], BaseTool]:
        """装饰器工厂：将普通函数注册为工具。

        Args:
            name: 工具名称。
            description: 工具描述。

        Returns:
            装饰器，将被装饰函数包装成 BaseTool 并注册。

        Example::

            @registry.tool(name="upper", description="将输入转为大写")
            def upper_tool(tool_input: str) -> str:
                return tool_input.upper()
        """
        def decorator(func: Callable[[str], str]) -> BaseTool:
            _name = name
            _desc = description

            class _FunctionTool(BaseTool):
                @property
                def name(self) -> str:  # type: ignore[override]
                    return _name

                @property
                def description(self) -> str:  # type: ignore[override]
                    return _desc

                def run(self, tool_input: str) -> str:
                    return func(tool_input)

            instance = _FunctionTool()
            self.register(instance)
            return instance

        return decorator

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
