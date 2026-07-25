"""
Agent 状态定义

LangGraph 状态机中流转的数据结构。
"""

from typing import TypedDict, List, Optional


class Step(TypedDict):
    """Agent 单步执行记录"""
    thought: str
    action: str
    action_input: str
    observation: str


class AgentState(TypedDict):
    """Agent 运行时的完整状态"""
    question: str                       # 用户原始问题
    messages: List[dict]                # LLM 消息历史
    steps: List[Step]                   # 执行步骤列表
    current_step: int                   # 当前步数
    intermediate_response: str          # 当前累积的 LLM 输出
    final_answer: Optional[str]         # 最终回答
    error: Optional[str]                # 错误信息
    max_steps: int                      # 最大步数
