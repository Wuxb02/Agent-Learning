"""
hello_agents.tools.async_executor
===================================

异步工具执行器（AsyncExecutor）模块。

AsyncExecutor 支持以下异步执行模式：
    - ``run_async``    : 将单个同步工具调用包装为协程（在线程池中运行）
    - ``run_parallel`` : 并发执行多个（工具, 输入）对，返回结果列表
    - ``run_batch``    : 对同一工具并发处理批量输入

所有工具本身仍为同步实现（继承 BaseTool），AsyncExecutor 通过
``asyncio.to_thread`` 在线程池中运行它们，避免阻塞事件循环。

典型用法::

    import asyncio
    from hello_agents.tools.async_executor import AsyncExecutor
    from hello_agents.tools.builtin.calculator import CalculatorTool

    executor = AsyncExecutor()
    tool = CalculatorTool()

    # 单个异步调用
    result = asyncio.run(executor.run_async(tool, "1 + 2"))

    # 批量并发
    results = asyncio.run(executor.run_batch(tool, ["1+1", "2+2", "3+3"]))
"""

from __future__ import annotations

import asyncio
from typing import Any

from hello_agents.tools.base import BaseTool
from hello_agents.core.exceptions import ToolExecutionError


class AsyncExecutor:
    """异步工具执行器。

    将同步 BaseTool 包装为异步协程并支持并发批量执行。

    Attributes:
        max_concurrency (int): 最大并发数，超出时通过 Semaphore 限流。
    """

    def __init__(self, max_concurrency: int = 10) -> None:
        """初始化执行器。

        Args:
            max_concurrency: 最大并发任务数，默认 10。
        """
        self.max_concurrency = max_concurrency
        self._semaphore: asyncio.Semaphore | None = None

    def _get_semaphore(self) -> asyncio.Semaphore:
        """懒加载 Semaphore（必须在事件循环内调用）。"""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)
        return self._semaphore

    async def run_async(self, tool: BaseTool, tool_input: str) -> str:
        """在线程池中异步执行单个工具。

        Args:
            tool: 要执行的工具实例。
            tool_input: 工具输入字符串。

        Returns:
            工具执行结果字符串。

        Raises:
            ToolExecutionError: 工具执行失败时抛出。
        """
        async with self._get_semaphore():
            try:
                return await asyncio.to_thread(tool.run, tool_input)
            except Exception as exc:
                raise ToolExecutionError(tool.name, exc) from exc

    async def run_parallel(
        self,
        tasks: list[tuple[BaseTool, str]],
    ) -> list[Any]:
        """并发执行多个（工具, 输入）对。

        Args:
            tasks: 元组列表，每个元素为 ``(tool, tool_input)``。

        Returns:
            与 tasks 顺序对应的结果列表；若某任务失败，对应位置为异常对象。
        """
        coroutines = [self.run_async(tool, inp) for tool, inp in tasks]
        return await asyncio.gather(*coroutines, return_exceptions=True)

    async def run_batch(
        self,
        tool: BaseTool,
        inputs: list[str],
    ) -> list[Any]:
        """对同一工具并发处理批量输入。

        Args:
            tool: 要执行的工具实例。
            inputs: 输入字符串列表。

        Returns:
            与 inputs 顺序对应的结果列表；若某任务失败，对应位置为异常对象。
        """
        tasks = [(tool, inp) for inp in inputs]
        return await self.run_parallel(tasks)
