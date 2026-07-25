"""
工具注册系统

所有工具统一注册，供 Agent 调用和生成描述。
"""

import re
from typing import Callable, Any


class Tool:
    def __init__(self, name: str, description: str, parameters: list[dict], func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def run(self, **kwargs) -> str:
        try:
            return str(self.func(**kwargs))
        except Exception as e:
            return f"[工具错误] {self.name}: {e}"

    def to_prompt(self) -> str:
        params = "\n".join([f"  - {p['name']} ({p['type']}): {p['description']}" for p in self.parameters])
        return f"## {self.name}\n{self.description}\n参数:\n{params}"


class ToolRegistry:
    _tools: dict[str, Tool] = {}

    @classmethod
    def register(cls, tool: Tool):
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> Tool:
        return cls._tools.get(name)

    @classmethod
    def all(cls) -> list[Tool]:
        return list(cls._tools.values())

    @classmethod
    def names(cls) -> str:
        return ", ".join(cls._tools.keys())

    @classmethod
    def descriptions(cls) -> str:
        return "\n\n".join([t.to_prompt() for t in cls._tools.values()])


def parse_action(text: str) -> tuple[str, dict] | None:
    """解析 Action: 工具名(参数名="参数值")"""
    match = re.search(r"Action:\s*(\w+)\s*\(([^)]*)\)", text, re.DOTALL)
    if not match:
        return None

    name = match.group(1)
    params_str = match.group(2).strip()
    params = {}

    for m in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', params_str):
        params[m.group(1)] = m.group(2)

    return name, params


def has_final_answer(text: str) -> str | None:
    """提取 Final Answer"""
    match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
    return match.group(1).strip() if match else None


def extract_thought(text: str) -> str:
    """提取 Thought"""
    match = re.search(r"Thought:\s*(.*?)(?=Action:|Final Answer:|$)", text, re.DOTALL)
    return match.group(1).strip() if match else ""
