# Odoo Debug MAS

Framework koordinasi Multi-Agent System berbasis Local LLM untuk debugging modul Odoo.

## Quick Start

```bash
# 1. Copy .env
cp .env.example .env

# 2. Edit .env - set LLM backend and model
#    For Ollama (local): LLM_BACKEND=ollama, OLLAMA_MODEL=qwen2.5-coder:7b
#    For API: LLM_BACKEND=openai, set OPENAI_API_KEY

# 3. Activate venv
source .venv/bin/activate

# 4. Debug single traceback
python main.py debug --traceback "ImportError: cannot import name 'account_move_line'..."

# 5. Run evaluation
python main.py evaluate --mode both
```

## Architecture

- **Orchestrator**: LangGraph (stateful cyclic graph)
- **Agents**: ErrorReader -> CodeTracer -> DocumentationChecker -> SolutionRecommender
- **LLM**: Ollama (local) or OpenAI-compatible API
- **Comparison**: MAS vs Single-Agent

## Dataset Format

Place JSON files in `dataset/` directory:

```json
[
  {
    "traceback": "Traceback (most recent call last):\n  File ...",
    "ground_truth": "Add 'account' to depends in __manifest__.py",
    "error_category": "import_error"
  }
]
```
