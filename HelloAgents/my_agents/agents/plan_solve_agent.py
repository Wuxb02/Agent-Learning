"""
hello_agents.agents.plan_solve_agent
======================================

PlanAndSolveAgent —— 先规划后执行的两阶段 Agent 实现。

Plan-and-Solve 范式将复杂任务分解为两个显式阶段：
    1. **规划 (Plan)**  : LLM 将用户任务分解为有序的子步骤列表。
    2. **执行 (Solve)** : 依次执行每个子步骤，每步的输出作为下一步的上下文。

相比 ReAct 的隐式推理链，Plan-and-Solve 的规划过程对用户透明，
适合需要审查中间步骤的场景。

参考论文: *Plan-and-Solve Prompting: Improving Zero-Shot
          Chain-of-Thought Reasoning* (Wang et al., 2023)

典型用法::

    agent = PlanAndSolveAgent(name="planner", llm=llm)
    result = agent.run("分析 2024 年全球 AI 发展趋势并给出三条建议")
    print(agent.last_plan)   # 查看生成的计划
"""

from __future__ import annotations

from typing import Optional

from my_agents.core.agent import Agent
from my_agents.core.config import Config
from my_agents.core.llm import HelloAgentsLLM
from my_agents.core.message import Message, MessageRole


class PlanAndSolveAgent(Agent):
    """先规划后执行的两阶段 Agent。

    Attributes:
        plan_prompt (str): 规划阶段系统提示词。
        solve_prompt (str): 执行阶段系统提示词。
        last_plan (list[str]): 最近一次 run() 生成的子步骤列表（调试用）。
    """

    _DEFAULT_PLAN = (
        "你是一个任务规划专家。请将用户的任务分解为清晰、有序的子步骤列表。"
        "每个步骤单独一行，以数字序号开头，例如：\n"
        "1. 收集数据\n2. 分析数据\n3. 得出结论"
    )
    _DEFAULT_SOLVE = (
        "你是一个任务执行专家。请根据已有的上下文，"
        "认真完成当前子步骤，并输出该步骤的执行结果。"
    )

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        plan_prompt: Optional[str] = None,
        solve_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> None:
        """初始化 PlanAndSolveAgent。

        Args:
            name: Agent 名称。
            llm: LLM 接口对象。
            plan_prompt: 覆盖默认的规划阶段系统提示词。
            solve_prompt: 覆盖默认的执行阶段系统提示词。
            config: 可选配置对象。
        """
        super().__init__(name=name, llm=llm, config=config)
        self.plan_prompt = plan_prompt or self._DEFAULT_PLAN
        self.solve_prompt = solve_prompt or self._DEFAULT_SOLVE
        self.last_plan: list[str] = []

    def run(self, user_input: str) -> str:
        """执行规划与逐步求解流程。

        Args:
            user_input: 用户输入的任务描述。

        Returns:
            整合所有子步骤结果后的最终回复文本。
        """
        # 阶段一：规划
        plan_text = self.llm.chat([
            Message.system(self.plan_prompt).to_dict(),
            {"role": "user", "content": user_input},
        ])
        self.last_plan = self._parse_steps(plan_text)

        # 阶段二：逐步执行
        context = f"原始任务：{user_input}\n\n规划步骤：\n{plan_text}\n\n"
        results: list[str] = []

        for idx, step in enumerate(self.last_plan, start=1):
            step_result = self.llm.chat([
                Message.system(self.solve_prompt).to_dict(),
                {
                    "role": "user",
                    "content": (
                        f"{context}"
                        f"当前步骤（{idx}/{len(self.last_plan)}）：{step}\n\n"
                        f"前序结果：\n" + "\n".join(results)
                    ),
                },
            ])
            results.append(f"步骤{idx}结果：{step_result}")

        final = self.llm.chat([
            Message.system("你是一个总结专家，请将以下各步骤结果整合为连贯的最终回复。").to_dict(),
            {
                "role": "user",
                "content": f"原始任务：{user_input}\n\n" + "\n\n".join(results),
            },
        ])

        self.add_message(MessageRole.USER, user_input)
        self.add_message(MessageRole.ASSISTANT, final)
        return final

    @staticmethod
    def _parse_steps(plan_text: str) -> list[str]:
        """从规划文本中提取子步骤列表。

        Args:
            plan_text: LLM 生成的规划文本。

        Returns:
            去除序号后的步骤描述字符串列表。
        """
        steps = []
        for line in plan_text.splitlines():
            line = line.strip()
            if not line:
                continue
            # 去除前缀序号，如 "1. " 或 "1) "
            if line and line[0].isdigit():
                line = line.lstrip("0123456789.-) ").strip()
            if line:
                steps.append(line)
        return steps
