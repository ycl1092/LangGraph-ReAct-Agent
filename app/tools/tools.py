"""
工具实现 — 包括 RAG 知识库查询
"""

import datetime


def _rag_query(query: str) -> str:
    """从知识库检索相关内容"""
    import sys
    from pathlib import Path
    rp = str(Path(__file__).resolve().parent.parent.parent.parent / "prod_rag")
    if rp not in sys.path:
        sys.path.insert(0, rp)
    from app.rag.vector_store import vector_store
    docs = vector_store.similarity_search_with_score(query, k=5)
    if not docs:
        return "知识库中未找到相关信息"
    results = []
    for doc, score in docs:
        src = doc.metadata.get("source", "未知")
        results.append(f"[来源: {src} | 相关度: {score:.3f}]\n{doc.page_content}")
    return "\n\n---\n\n".join(results)


def _get_current_time(location: str = "北京") -> str:
    tz_map = {"北京": 8, "上海": 8, "纽约": -5, "伦敦": 0, "东京": 9, "悉尼": 11, "巴黎": 1}
    tz = tz_map.get(location, 8)
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    local = utc_now + datetime.timedelta(hours=tz)
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return (f"{location} 的当前时间:\n"
            f"  {local.strftime('%Y年%m月%d日 %H:%M:%S')}\n"
            f"  {weekdays[local.weekday()]}\n"
            f"  时区: UTC{'+' if tz >= 0 else ''}{tz}")


def _query_weather(city: str = "北京", date: str = "今天") -> str:
    db = {
        "北京": {"今天": "晴 15-25°C 空气质量良", "明天": "多云 16-26°C", "后天": "小雨 14-22°C"},
        "上海": {"今天": "阴转小雨 18-23°C", "明天": "小雨 17-22°C", "后天": "多云 18-24°C"},
        "深圳": {"今天": "多云 22-28°C", "明天": "阵雨 21-27°C", "后天": "晴 23-29°C"},
        "厦门": {"今天": "晴 20-26°C 非常适合出门", "明天": "晴转多云 21-27°C", "后天": "多云 20-26°C"},
    }
    info = db.get(city, {}).get(date, f"没有 {date} 的预报数据")
    return f"{city} {date} 天气预报:\n  {info}"


def _calculate(expression: str) -> str:
    allowed = set("0123456789+-*/().% ")
    if not all(c in allowed for c in expression):
        return "[错误] 表达式包含不支持的字符"
    try:
        r = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {r}"
    except ZeroDivisionError:
        return "[错误] 除数不能为0"
    except Exception as e:
        return f"[错误] {e}"


def register_all_tools(registry):
    from app.tools.registry import Tool
    registry.register(Tool(
        name="rag_query",
        description="从知识库中检索相关信息。当用户的问题涉及产品知识、说明书、维修保养等知识库内容时使用。",
        parameters=[{"name": "query", "type": "string", "description": "检索关键词或问题"}],
        func=_rag_query,
    ))
    registry.register(Tool(
        name="get_current_time",
        description="获取指定城市或地点的当前日期和时间。",
        parameters=[{"name": "location", "type": "string", "description": "城市名称"}],
        func=_get_current_time,
    ))
    registry.register(Tool(
        name="query_weather",
        description="查询指定城市和日期的天气情况。",
        parameters=[
            {"name": "city", "type": "string", "description": "城市名称"},
            {"name": "date", "type": "string", "description": "日期：'今天'/'明天'/'后天'"},
        ],
        func=_query_weather,
    ))
    registry.register(Tool(
        name="calculate",
        description="执行数学计算。支持 + - * / ( ) %",
        parameters=[{"name": "expression", "type": "string", "description": "数学表达式"}],
        func=_calculate,
    ))
