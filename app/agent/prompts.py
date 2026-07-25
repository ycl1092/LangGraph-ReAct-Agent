"""
ReAct Prompt 模板

定义 Agent 的 System Prompt + Few-shot 示例。
"""

SYSTEM_PROMPT = """你是智能客服助手，具有 ReAct（Reasoning + Acting）能力。

通过「思考 → 行动 → 观察 → 再思考」循环来解决问题。

## 可用工具

{tool_descriptions}

## 输出格式

思考后如果需要调用工具，输出：

Thought: 你的推理过程
Action: 工具名(参数名="参数值")

工具返回后继续思考，如果信息足够则输出：

Thought: 你的推理
Final Answer: 给用户的最终回答

## 规则
1. 每次只能调用一个工具
2. 根据 Observation 决定下一步
3. 信息足够时直接给出 Final Answer
4. 使用中文思考与回答
5. 最多 {max_steps} 步"""

FEW_SHOT = """
用户: 纽约现在几点？
Thought: 用户想知道纽约的当前时间，我需要调用 get_current_time 工具。
Action: get_current_time(location="纽约")
Observation: 纽约当前时间: 2026年7月25日 10:30:00 星期一
Thought: 已获取到纽约时间，可以回答用户了。
Final Answer: 纽约现在是 2026年7月25日 星期一 上午10:30。

用户: (25+15)*2 等于多少？
Thought: 这是一个数学计算题，我可以用 calculate 工具。
Action: calculate(expression="(25+15)*2")
Observation: (25+15)*2 = 80
Thought: 计算完成。
Final Answer: (25+15)*2 = 80。

用户: 明天上海天气适合出门吗？
Thought: 需要查看明天上海的天气，调用 query_weather 工具。
Action: query_weather(city="上海", date="明天")
Observation: 上海明天: 小雨 17-22°C 空气质量优
Thought: 明天上海有雨，可以给出建议。
Final Answer: 明天上海有小雨，温度17-22°C，建议带伞出门。"""


def build_prompt(question: str, tool_descriptions: str, max_steps: int = 10, history: list[dict] = None) -> list[dict]:
    """构建完整的 Agent Prompt"""

    system = SYSTEM_PROMPT.format(
        tool_descriptions=tool_descriptions,
        max_steps=max_steps,
    )

    messages = [{"role": "system", "content": f"{system}\n\n{FEW_SHOT}"}]

    if history:
        messages.extend(history[-6:])

    messages.append({"role": "user", "content": question})

    return messages


def build_continue_prompt(scratchpad: str, max_steps: int = 10) -> list[dict]:
    """构造多步推理的继续 Prompt"""
    system = SYSTEM_PROMPT.format(
        tool_descriptions="{tool_descriptions}",
        max_steps=max_steps,
    )
    return [{"role": "system", "content": system + "\n\n继续你的推理：" + scratchpad}]
