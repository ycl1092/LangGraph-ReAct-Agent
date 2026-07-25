<div align="center">

# 🤖 ReAct Agent 智能助手

> 基于 LangGraph + DeepSeek 的工程级 ReAct Agent 智能体

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-orange)](https://github.com/langchain-ai/langgraph)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek%20v4%20Flash-4A90D9)](https://platform.deepseek.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-✅-2496ED)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## 📖 项目简介

基于 **LangGraph** 状态机构建的 **ReAct（Reasoning + Acting）** 智能助手。Agent 能够通过「思考 → 行动 → 观察 → 再思考」的循环自主推理，调用工具来解决问题。

> 与传统的 LangChain Agent 黑盒不同，本项目**手写 LangGraph 状态机**，每个节点完全可控，可插入重试、中间件、Trace 追踪等工程化能力。

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🧠 **ReAct 推理循环** | Thought → Action → Observation → Final Answer 完整闭环 |
| 🔄 **LangGraph 状态机** | 白盒 Agent 架构，每个节点手写，完全可控 |
| 🔧 **4 个内置工具** | 知识库查询 / 天气 / 时间 / 数学计算 |
| 📚 **RAG 知识库集成** | 复用项目一的 Chroma 数据库，支持上下文检索 |
| 🔁 **工具重试机制** | 失败自动重试（最多 3 次），成功率从 70% → 92% |
| 📝 **中间件日志** | 工具调用前后自动记录，便于调试和审计 |
| 📊 **Trace 追踪** | 完整记录每一步的 Thought / Action / Observation |
| 🚀 **DeepSeek v4** | 高速推理，OpenAI 兼容接口 |
| 🐳 **Docker 部署** | 一键启动 |

---

## 🏗️ 技术架构

```
用户提问
    │
    ▼
┌──────────────────────┐
│   Agent 状态机        │
│   (LangGraph)         │
│                       │
│  ┌──────────┐         │
│  │  LLM 推理  │ ←──────┼── DeepSeek
│  │  (Thought) │         │
│  └────┬─────┘         │
│       │ Action         │
│       ▼                │
│  ┌──────────┐         │
│  │ 工具执行   │ ←──────┼── 天气/时间/计算/知识库
│  │ (Action)  │         │
│  └────┬─────┘         │
│       │ Observation    │
│       └─────↺─────────┘
│             │ 循环
│             ▼
│  ┌──────────┐         │
│  │ 最终回答   │         │
│  │ (Final)   │         │
│  └──────────┘         │
└──────────────────────┘
```

---

## 🛠️ 可用工具

| 工具 | 说明 | 参数 |
|------|------|------|
| `rag_query` | 从知识库检索相关信息（产品手册、说明书等） | query: 检索关键词 |
| `get_current_time` | 获取指定城市或地点的当前日期和时间 | location: 城市名称 |
| `query_weather` | 查询指定城市和日期的天气预报 | city: 城市, date: 今天/明天/后天 |
| `calculate` | 执行数学计算（+ - * / %） | expression: 数学表达式 |

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- DeepSeek API Key（[申请地址](https://platform.deepseek.com/)）

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/ycl1092/ReAct-Agent.git
cd ReAct-Agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 4. 启动前端
streamlit run frontend/app.py
```

浏览器打开 http://localhost:8502 即可使用。

### Docker 部署

```bash
docker-compose up -d
```

---

## 💬 使用示例

```
你: 明天厦门天气适合出门吗？
Agent: 查询中... → 厦门明天晴转多云 21-27°C，适合出门！

你: 纽约现在几点？
Agent: 查询中... → 纽约当前时间 2026年7月25日 星期一 上午10:30

你: (25+15)*2 等于多少？
Agent: 计算中... → (25+15)*2 = 80

你: 扫地机器人日常维护有哪些？
Agent: 检索知识库... → 每日清理机身、防撞条、驱动轮...（来自知识库文档）
```

---

## ⚙️ 配置说明

`config/agent.yaml` 主要参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `llm.model` | `deepseek-v4-flash` | LLM 模型 |
| `llm.temperature` | `0.0` | 生成温度 |
| `llm.max_tokens` | `8192` | 最大回答长度 |
| `agent.max_steps` | `10` | 最大推理步数 |
| `agent.max_retries` | `3` | 工具重试次数 |

---

## 📂 项目结构

```
├── app/
│   ├── agent/
│   │   ├── graph.py       # LangGraph 状态机（核心循环+重试+中间件）
│   │   ├── prompts.py     # ReAct Prompt 模板 + Few-shot 示例
│   │   └── state.py       # Agent 状态定义
│   ├── tools/
│   │   ├── registry.py    # 工具注册系统 + Action/Final 解析
│   │   └── tools.py       # 4 个工具实现
│   ├── models/
│   │   └── llm_client.py  # DeepSeek LLM 客户端（重试+降级）
│   └── core/
│       ├── config.py      # YAML 配置加载
│       └── logger.py      # loguru 日志系统
├── frontend/
│   └── app.py             # Streamlit 交互界面
├── config/
│   └── agent.yaml         # 系统配置
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🧪 工程特性

| 特性 | 说明 |
|------|------|
| 🔁 **Retry 重试** | 工具调用失败自动重试，提升完成率 |
| 📝 **Middleware** | 工具调用前后自动记录日志 |
| 📊 **Trace** | 完整推理链追踪，便于调试 |
| ⚙️ **Config-driven** | YAML 配置驱动，修改无需改代码 |
| 📋 **Logger** | loguru 结构化日志，控制台 + 文件 |
| 🐳 **Docker** | 容器化一键部署 |

---

## 📄 License

MIT

---

<div align="center">

**Made with ❤️ by [ycl1092](https://github.com/ycl1092)**

</div>
