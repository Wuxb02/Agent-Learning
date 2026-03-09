"""
hello_agents.tools.builtin
===========================

内置工具集，提供开箱即用的常用工具。

当前内置工具:
    - ``CalculatorTool`` : 安全的数学表达式计算工具
    - ``SearchTool``     : 关键词搜索工具（默认使用模拟实现，可替换为真实 API）
"""

from hello_agents.tools.builtin.calculator import CalculatorTool
from hello_agents.tools.builtin.search import SearchTool

__all__ = ["CalculatorTool", "SearchTool"]
