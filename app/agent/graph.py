import time
from typing import Literal
from app.core.logger import logger
from app.models.llm_client import llm
from app.agent.prompts import build_prompt
from app.agent.state import AgentState, Step
from app.tools.registry import ToolRegistry, parse_action, has_final_answer, extract_thought

MAX_RETRIES = 3

def _trace(step_data: dict):
    logger.info(f"[Trace] Step {step_data['step']}: {step_data['thought'][:50]}... -> {step_data['action']}")

def _llm_step(state, tools_desc):
    messages = build_prompt(question=state["question"], tool_descriptions=tools_desc, max_steps=state["max_steps"], history=state["messages"][:-1] if state["messages"] else None)
    if state["steps"]:
        sp = ""
        for s in state["steps"]:
            sp += f"Thought: {s['thought']}\nAction: {s['action']}({s['action_input']})\nObservation: {s['observation']}\n"
        sp += "Thought: "
        messages.append({"role": "assistant", "content": sp})
    response = llm.chat(messages)
    state["intermediate_response"] = response
    fa = has_final_answer(response)
    if fa:
        state["final_answer"] = fa
    return state

def _tool_step(state):
    response = state["intermediate_response"]
    ai = parse_action(response)
    if not ai:
        if not state.get("final_answer"):
            state["final_answer"] = state.get("intermediate_response", "无法解析")
        return state
    tool_name, params = ai
    tool = ToolRegistry.get(tool_name)
    if not tool:
        obs = "[错误] 未知工具"
    else:
        retry_count = 0
        while retry_count <= MAX_RETRIES:
            if retry_count > 0:
                logger.info(f"  [重试 {retry_count}/{MAX_RETRIES}]")
            logger.info(f"[中间件] -> {tool_name}({params})")
            obs = tool.run(**params)
            logger.info(f"[中间件] <- {obs[:60]}...")
            if not obs.startswith("[错误]"):
                break
            retry_count += 1
            time.sleep(1)
    thought = extract_thought(response) or ""
    state["steps"].append(Step(thought=thought, action=tool_name, action_input=str(params), observation=obs))
    state["current_step"] += 1
    _trace({"step": state["current_step"], "thought": thought, "action": f"{tool_name}({params})"})
    return state

def router(state):
    if state.get("final_answer"):
        return "__end__"
    if state["current_step"] >= state["max_steps"]:
        return "__end__"
    if parse_action(state.get("intermediate_response", "")):
        return "tools"
    return "__end__"

def build_agent_graph():
    from langgraph.graph import StateGraph, END
    td = ToolRegistry.descriptions()
    b = StateGraph(AgentState)
    b.add_node("agent", lambda s: _llm_step(s, td))
    b.add_node("tools", _tool_step)
    b.set_entry_point("agent")
    b.add_conditional_edges("agent", router, {"tools": "tools", END: END})
    b.add_edge("tools", "agent")
    return b.compile(), td

def run_agent(question):
    g, _ = build_agent_graph()
    init = {"question": question, "messages": [{"role": "user", "content": question}], "steps": [], "current_step": 0, "intermediate_response": "", "final_answer": None, "error": None, "max_steps": 10}
    try:
        r = g.invoke(init)
        if not r.get("final_answer") and r.get("intermediate_response"):
            r["final_answer"] = r["intermediate_response"][:300]
        if not r.get("final_answer"):
            r["final_answer"] = "(无回答)"
        return r
    except Exception as e:
        logger.error(f"Agent失败: {e}")
        init["final_answer"] = f"系统错误: {e}"
        return init
