"""
LLM 客户端 — 支持 DeepSeek，带重试
"""

import time
from typing import Optional
from openai import OpenAI
from app.core.config import settings
from app.core.logger import logger


class LLMClient:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = getattr(settings, "LLM_MODEL", "deepseek-v4-flash")
        self.temperature = getattr(settings, "LLM_TEMPERATURE", 0.0)
        self.max_tokens = getattr(settings, "LLM_MAX_TOKENS", 4096)

        if not self.api_key:
            logger.warning("API Key 未配置")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, messages: list[dict]) -> str:
        if self.client is None:
            return self._mock(messages)

        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"LLM 调用失败 (第{attempt+1}次): {e}")
                if attempt < 2:
                    time.sleep(1 + attempt)
                else:
                    logger.error(f"降级到 Mock: {e}")
                    return self._mock(messages)

    def _mock(self, messages):
        return "（Mock）请配置 API Key 后使用真实调用。"

    @property
    def is_ready(self):
        return self.client is not None


llm = LLMClient()
