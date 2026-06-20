from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from state.debug_state import DebugState
from agents.error_reader import error_reader_node
from agents.code_tracer import code_tracer_node
from agents.documentation_checker import documentation_checker_node
from agents.solution_recommender import solution_recommender_node

MAX_RETRIES = 1


def _should_retry(state: DebugState) -> str:
    """Conditional edge: retry Code Tracer if doc check fails and retries remain."""
    verification = state.get("doc_verification", "").lower()
    retry_count = state.get("retry_count", 0)
    if "no" in verification and retry_count < MAX_RETRIES:
        return "retry"
    return "continue"


def build_mas_graph():
    """Build the Multi-Agent System graph using LangGraph."""
    g = StateGraph(DebugState)

    g.add_node("error_reader", error_reader_node)
    g.add_node("code_tracer", code_tracer_node)
    g.add_node("documentation_checker", documentation_checker_node)
    g.add_node("solution_recommender", solution_recommender_node)

    g.add_edge(START, "error_reader")
    g.add_edge("error_reader", "code_tracer")
    g.add_edge("code_tracer", "documentation_checker")

    g.add_conditional_edges(
        "documentation_checker",
        _should_retry,
        {
            "retry": "code_tracer",
            "continue": "solution_recommender",
        },
    )

    g.add_edge("solution_recommender", END)

    return g.compile()
