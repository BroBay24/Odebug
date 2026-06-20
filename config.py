import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")

    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    ODOO_ADDONS_PATH = os.getenv("ODOO_ADDONS_PATH", "")
    DATASET_PATH = os.getenv("DATASET_PATH", os.path.join(os.path.dirname(__file__), "dataset"))
    RESULTS_PATH = os.getenv("RESULTS_PATH", os.path.join(os.path.dirname(__file__), "results"))
