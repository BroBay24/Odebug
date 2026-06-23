import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")

    # Default model (fallback if per-agent model not set)
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

    # Per-agent model configuration (multi-model MAS)
    # Each agent can use a different model suited to its role.
    AGENT_MODEL_ERROR_READER = os.getenv("AGENT_MODEL_ERROR_READER", "qwen2.5-coder:7b")
    AGENT_MODEL_CODE_TRACER = os.getenv("AGENT_MODEL_CODE_TRACER", "qwen2.5-coder:7b")
    AGENT_MODEL_DOC_CHECKER = os.getenv("AGENT_MODEL_DOC_CHECKER", "qwen2.5-coder:7b")
    AGENT_MODEL_SOLUTION_RECOMMENDER = os.getenv(
        "AGENT_MODEL_SOLUTION_RECOMMENDER",
        "yuxinlu1/gemma-4-12b-agentic-fable5-composer2.5-v2-3.5x-tau2-GGUF:Q4_K_M",
    )

    # Single-agent baseline model
    AGENT_MODEL_SINGLE = os.getenv("AGENT_MODEL_SINGLE", "qwen2.5-coder:7b")

    # OpenAI-compatible API (fallback/testing)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    ODOO_ADDONS_PATH = os.getenv("ODOO_ADDONS_PATH", "")
    DATASET_PATH = os.getenv("DATASET_PATH", os.path.join(os.path.dirname(__file__), "dataset"))
    RESULTS_PATH = os.getenv("RESULTS_PATH", os.path.join(os.path.dirname(__file__), "results"))
