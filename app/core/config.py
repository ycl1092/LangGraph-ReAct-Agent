import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# 显式指定 .env 路径（相对于此文件的位置）
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        self.ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        config_path = self.ROOT_DIR / "config" / "agent.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"配置不存在: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            self._raw = yaml.safe_load(f)

        self._flatten(self._raw)

        self.LLM_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY", "")
        self.LLM_BASE_URL = os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com/v1"

    def _flatten(self, d, prefix=""):
        for k, v in d.items():
            key = f"{prefix}{k}".upper() if prefix else k.upper()
            if isinstance(v, dict):
                self._flatten(v, f"{key}_")
            else:
                setattr(self, key, v)

    def get(self, path, default=None):
        parts = path.split(".")
        val = self._raw
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return default
        return val if val is not None else default


settings = Settings()
