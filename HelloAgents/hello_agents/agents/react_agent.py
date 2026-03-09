"""
hello_agents.agents.react_agent
================================

ReActAgent —— 基于 Reason + Act 范式的 Agent 实现。

ReAct（Reasoning + Acting）是一种让 Agent 交替进行"思考"与"行动"的推理框架：
    1. **Thought**  : LLM 分析当前状态，决定下一步行动。
    2. **Action**   : 调用对应工具，获取观察结果（Observation）。
    3. **Observation**: 将工具结果反馈给 LLM，进入下一轮 Thought。
    4. 当 LLM 输出 ``Final Answer:`` 时终止循环。

参考论文: *ReAct: Synergizing Reasoning and Acting in Language Models*
          (Yao et al., 2023)

典型用法::

    from hello_agents.agents.react_agent import ReActAgent
    from hello_agents.tools.registry import ToolRegistry
    from hello_agents.tools.builtin.calculator import CalculatorTool

    registry = ToolRegistry()
    registry.register(CalculatorTool())

    agent = ReActAgent(name="react", llm=llm, tool_registry=registry)
    answer = agent.run("计算 (123 + 456) * 2 的结果")
"""

from __future__ import annotations

import re
from typing import Optional

from hello_agents.core.agent import Agent
from hello_agents.core.config import Config
from hello_agents.core.exceptions import MaxStepsExceeded
from hello_agents.core.llm import HelloAgentsLLM
from hello_agents.core.message import Message, MessageRole
from hello_agents.tools.registry import ToolRegistry

_FINAL_ANSWER_RE = re.compile(r"Final Answer:\s*(.*)", re.IGNORECASE | re.DOTALL)
_ACTION_RE = re.compile(r"Action:\s*(\w+)\[(.+?)\]", re.DOTALL)


class ReActAgent(Agent):
    """Reason + Act 交替循环的 Agent。

    在每个推理步中，Agent 先输出 Thought（思考），再输出 Action（行动），
    执行工具后将 Observation（观察结果）注入上下文，循环直至输出最终答案。

    Attributes:
        tool_registry (ToolRegistry): 可用工具的注册表。
        system_prompt (str): 系统提示词，包含 ReAct 格式说明。
    """

    _DEFAULT_SYSTEM = (
        "你是一个使用 ReAct 框架的智能助手。\n"
        "每一步按如下格式输出：\n"
        "Thought: <你的思考过程>\n"
        "Action: <工具名称>[<工具参数>]\n"
        "当你有最终答案时输出：\n"
        "Final Answer: <最终答案>"
    )

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> None:
        """初始化 ReActAgent。

        Args:
            name: Agent 名称。
            llm: LLM 接口对象。
            tool_registry: 已注册可用工具的注册表。
            system_prompt: 覆盖默认的系统提示词；None 则使用内置模板。
            config: 可选配置对象。
        """
        super().__init__(name=name, llm=llm, config=config)
        self.tool_registry = tool_registry
        self.system_prompt = system_prompt or self._DEFAULT_SYSTEM

    def run(self, user_input: str) -> str:
        """执行 ReAct 推理循环。

        Args:
            user_input: 用户问题或任务描述。

        Returns:
            最终答案字符串。

        Raises:
            MaxStepsExceeded: 超过 config.max_steps 步仍未得到最终答案时抛出。
        """
        self.add_message(MessageRole.USER, user_input)

        for step in range(self.config.max_steps):
            messages = [
                Message.system(self.system_prompt).to_dict(),
                *[m.to_dict() for m in self._history],
            ]
            response = self.llm.chat(messages)
            self.add_message(MessageRole.ASSISTANT, response)

            # 检查是否已得出最终答案
            final_match = _FINAL_ANSWER_RE.search(response)
            if final_match:
                return final_match.group(1).strip()

            # 解析 Action 并执行对应工具
            action_match = _ACTION_RE.search(response)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_input = action_match.group(2).strip()
                observation = self._execute_tool(tool_name, tool_input)
                self.add_message(
                    MessageRole.USER,
                    f"Observation: {observation}",
                )

        raise MaxStepsExceeded(
            f"ReActAgent '{self.name}' 超过最大步数 {self.config.max_steps}"
        )

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """查找并执行指定工具。

        Args:
            tool_name: 工具名称（与注册表中的 name 属性一致）。
            tool_input: 传递给工具的原始字符串参数。

        Returns:
            工具执行结果的字符串表示；若工具不存在则返回错误描述。
        """
        try:
            tool = self.tool_registry.get(tool_name)
            return str(tool.run(tool_input))
        except Exception as exc:  # noqa: BLE001
            return f"工具执行错误: {exc}"
