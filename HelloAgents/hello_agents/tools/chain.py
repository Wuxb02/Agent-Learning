"""
hello_agents.tools.chain
=========================

工具链管理系统（ToolChain）模块。

ToolChain 允许将多个工具串联成流水线：
    前一个工具的输出作为后一个工具的输入，
    最终返回链尾工具的执行结果。

支持两种构建方式：
    1. 实例化时传入工具列表。
    2. 使用 ``>>`` 运算符动态追加工具。

典型用法::

    from hello_agents.tools.chain import ToolChain
    from hello_agents.tools.builtin.calculator import CalculatorTool
    from hello_agents.tools.builtin.search import SearchTool

    # 方式一：构造时传入
    chain = ToolChain([CalculatorTool(), SearchTool()])

    # 方式二：运算符追加
    chain = ToolChain() >> CalculatorTool() >> SearchTool()

    result = chain.run("3 + 4")
"""

from __future__ import annotations

from hello_agents.tools.base import BaseTool
from hello_agents.core.exceptions import ToolExecutionError


class ToolChain:
    """工具链管理系统。

    将多个 BaseTool 串联执行，前一工具的输出传递给后一工具。

    Attributes:
        _tools (list[BaseTool]): 按执行顺序排列的工具列表。
    """

    def __init__(self, tools: list[BaseTool] | None = None) -> None:
        """初始化工具链。

        Args:
            tools: 初始工具列表，按顺序执行；None 则创建空链。
        """
        self._tools: list[BaseTool] = tools or []

    def add(self, tool: BaseTool) -> "ToolChain":
        """向链尾追加一个工具（原地修改）。

        Args:
            tool: 要追加的工具实例。

        Returns:
            self，支持链式调用。
        """
        self._tools.append(tool)
        return self

    def __rshift__(self, tool: BaseTool) -> "ToolChain":
        """``>>`` 运算符重载，返回追加工具后的新 ToolChain（不可变风格）。

        Args:
            tool: 要追加的工具实例。

        Returns:
            包含新工具的新 ToolChain 实例。
        """
        new_chain = ToolChain(list(self._tools))
        new_chain.add(tool)
        return new_chain

    def run(self, initial_input: str) -> str:
        """按顺序依次执行链中所有工具。

        Args:
            initial_input: 传入链首工具的初始输入。

        Returns:
            链尾工具的输出字符串。

        Raises:
            ValueError: 若工具链为空则抛出。
            ToolExecutionError: 若链中某个工具执行失败则抛出，
                包含工具名称与原始异常信息。
        """
        if not self._tools:
            raise ValueError("ToolChain 为空，至少需要一个工具。")

        result = initial_input
        for tool in self._tools:
            try:
                result = tool.run(result)
            except Exception as exc:
                raise ToolExecutionError(tool.name, exc) from exc
        return result

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        names = " >> ".join(t.name for t in self._tools)
        return f"ToolChain({names})"
