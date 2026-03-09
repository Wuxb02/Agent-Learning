"""
hello_agents.tools.builtin.calculator
=======================================

CalculatorTool —— 安全的数学表达式计算工具。

本工具接收一个数学表达式字符串，使用 Python ``ast`` 模块
在沙盒环境中进行安全求值（不执行任意代码），并返回计算结果。

支持的运算:
    - 加 ``+``、减 ``-``、乘 ``*``、除 ``/``、整除 ``//``
    - 取模 ``%``、幂运算 ``**``
    - 一元正负号 ``+x``、``-x``
    - 括号分组

不支持（会抛出 ValueError）:
    - 函数调用（如 ``eval``、``exec``）
    - 变量引用
    - 比较/布尔/位运算

典型用法（Agent 调用格式）::

    Action: calculator[(123 + 456) * 2]
    # → "1158"

    Action: calculator[2 ** 10]
    # → "1024"
"""

from __future__ import annotations

import ast
import operator
from typing import Union

from hello_agents.tools.base import BaseTool

# 允许的二元运算符映射
_BINARY_OPS: dict[type, object] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# 允许的一元运算符映射
_UNARY_OPS: dict[type, object] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

Number = Union[int, float]


def _safe_eval(node: ast.AST) -> Number:
    """递归安全求值 AST 节点。

    Args:
        node: 待求值的 AST 节点。

    Returns:
        数值计算结果（int 或 float）。

    Raises:
        ValueError: 遇到不支持的表达式类型时抛出。
        ZeroDivisionError: 除以零时透传。
    """
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"不支持的常量类型: {type(node.value)}")
    if isinstance(node, ast.BinOp):
        op_func = _BINARY_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return op_func(left, right)  # type: ignore[operator]
    if isinstance(node, ast.UnaryOp):
        op_func = _UNARY_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"不支持的一元运算符: {type(node.op).__name__}")
        return op_func(_safe_eval(node.operand))  # type: ignore[operator]
    raise ValueError(f"不支持的表达式类型: {type(node).__name__}")


class CalculatorTool(BaseTool):
    """安全的数学表达式计算工具。

    使用 AST 白名单机制对输入表达式进行安全求值，
    避免执行任意 Python 代码。
    """

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "计算数学表达式并返回结果。"
            "输入格式：数学表达式字符串，如 '(3 + 4) * 2'。"
            "支持 +、-、*、/、//、%、** 及括号。"
        )

    def run(self, tool_input: str) -> str:
        """计算输入的数学表达式。

        Args:
            tool_input: 数学表达式字符串，如 ``"(3 + 4) * 2"``。

        Returns:
            计算结果的字符串表示；发生错误时返回错误描述。
        """
        try:
            tree = ast.parse(tool_input.strip(), mode="eval")
            result = _safe_eval(tree)
            # 整数结果去除小数点
            if isinstance(result, float) and result.is_integer():
                return str(int(result))
            return str(result)
        except ZeroDivisionError:
            return "错误：除以零"
        except (ValueError, SyntaxError) as exc:
            return f"表达式错误：{exc}"
