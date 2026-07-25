import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.registry import ToolRegistry
from app.tools.tools import register_all_tools
from app.agent.graph import run_agent

register_all_tools(ToolRegistry)

st.set_page_config(page_title="ReAct Agent", page_icon="")
st.title(" ReAct Agent 智能助手")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("请输入问题..."):
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            result = run_agent(prompt)
            answer = result.get("final_answer", "无回答")
            st.markdown(answer)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.sidebar:
    st.header("信息")
    st.caption(f"工具: {ToolRegistry.names()}")
    st.caption(f"模型: deepseek-v4-flash")
    st.caption(f"步数: {len(result.get('steps', []))}") if prompt else None
    if st.button("清除对话"):
        st.session_state.messages = []
        st.rerun()
    st.caption(f"步数: {len(result.get('steps', []))}") if prompt else None
    if prompt:
        try:
            st.caption(f"步数: {len(result.get('steps', []))}")
        except Exception:
            pass
