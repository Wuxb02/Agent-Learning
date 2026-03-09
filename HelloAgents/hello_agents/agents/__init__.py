"""
hello_agents.agents
===================

Agent 实现层，提供多种开箱即用的 Agent 推理范式。

导出:
    SimpleAgent        —— 单轮/多轮对话型 Agent，无复杂推理循环
    ReActAgent         —— Reason + Act 交替循环的 Agent
    ReflectionAgent    —— 带自我反思与输出修订能力的 Agent
    PlanAndSolveAgent  —— 先规划后执行的两阶段 Agent
"""

from hello_agents.agents.simple_agent import SimpleAgent
from hello_agents.agents.react_agent import ReActAgent
from hello_agents.agents.reflection_agent import ReflectionAgent
from hello_agents.agents.plan_solve_agent import PlanAndSolveAgent

__all__ = [
    "SimpleAgent",
    "ReActAgent",
    "ReflectionAgent",
    "PlanAndSolveAgent",
]
