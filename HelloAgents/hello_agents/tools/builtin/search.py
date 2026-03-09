"""
hello_agents.tools.builtin.search
===================================

SearchTool —— 关键词搜索工具。

本模块提供一个可扩展的搜索工具骨架：
    - 默认实现（``MockSearchBackend``）返回模拟结果，适合开发与测试。
    - 生产环境可通过实现 ``SearchBackend`` 协议并注入 ``SearchTool``
      来切换为真实的搜索 API（如 Google、Bing、DuckDuckGo 等）。

工具输入格式::

    关键词字符串，例如 "Python asyncio tutorial"

工具输出格式::

    搜索结果摘要字符串，多条结果以换行分隔。

典型用法（Agent 调用格式）::

    Action: search[Python asyncio best practices 2024]
    # → "1. Real Python: AsyncIO in Python...\n2. ..."

替换后端示例::

    class BingBackend(SearchBackend):
        def search(self, query: str, top_k: int) -> list[dict]:
            # 调用 Bing Search API ...
            ...

    tool = SearchTool(backend=BingBackend(), top_k=5)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from hello_agents.tools.base import BaseTool


@runtime_checkable
class SearchBackend(Protocol):
    """搜索后端协议。

    任何实现了 ``search`` 方法的对象均可作为 SearchTool 的后端。

    ``search`` 方法应返回字典列表，每条字典包含：
        - ``title``   : 结果标题
        - ``snippet`` : 内容摘要
        - ``url``     : 来源链接（可选）
    """

    def search(self, query: str, top_k: int) -> list[dict]:
        """执行搜索并返回结果列表。

        Args:
            query: 搜索关键词。
            top_k: 返回结果数量上限。

        Returns:
            结果字典列表。
        """
        ...


class MockSearchBackend:
    """模拟搜索后端，返回占位结果，用于开发与测试。"""

    def search(self, query: str, top_k: int) -> list[dict]:
        """返回包含查询关键词的模拟搜索结果。

        Args:
            query: 搜索关键词。
            top_k: 返回结果数量上限。

        Returns:
            模拟的结果字典列表。
        """
        return [
            {
                "title": f"[模拟结果 {i}] 关于 '{query}' 的内容",
                "snippet": (
                    f"这是关于 '{query}' 的模拟搜索结果第 {i} 条。"
                    "在生产环境中请替换为真实的搜索 API 后端。"
                ),
                "url": f"https://example.com/search?q={query}&result={i}",
            }
            for i in range(1, top_k + 1)
        ]


class SearchTool(BaseTool):
    """关键词搜索工具。

    通过可插拔的 ``SearchBackend`` 执行搜索，并将结果格式化为字符串。

    Attributes:
        backend (SearchBackend): 搜索后端实例。
        top_k (int): 返回搜索结果的数量上限。
    """

    def __init__(
        self,
        backend: SearchBackend | None = None,
        top_k: int = 3,
    ) -> None:
        """初始化 SearchTool。

        Args:
            backend: 搜索后端；None 则使用 MockSearchBackend。
            top_k: 返回结果数量上限，默认 3。
        """
        self.backend: SearchBackend = backend or MockSearchBackend()
        self.top_k = top_k

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return (
            "搜索互联网信息并返回相关摘要。"
            f"输入格式：搜索关键词字符串。最多返回 {self.top_k} 条结果。"
        )

    def run(self, tool_input: str) -> str:
        """执行关键词搜索。

        Args:
            tool_input: 搜索关键词字符串。

        Returns:
            格式化后的搜索结果字符串；发生错误时返回错误描述。
        """
        try:
            results = self.backend.search(tool_input.strip(), self.top_k)
            if not results:
                return f"未找到关于 '{tool_input}' 的搜索结果。"

            lines: list[str] = []
            for idx, item in enumerate(results, start=1):
                title = item.get("title", "（无标题）")
                snippet = item.get("snippet", "")
                url = item.get("url", "")
                line = f"{idx}. {title}\n   {snippet}"
                if url:
                    line += f"\n   来源: {url}"
                lines.append(line)

            return "\n\n".join(lines)
        except Exception as exc:  # noqa: BLE001
            return f"搜索失败：{exc}"
