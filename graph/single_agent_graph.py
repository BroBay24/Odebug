from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from state.debug_state import DebugState
from agents.single_agent import single_agent_node


def build_single_agent_graph():
    """Build the Single-Agent baseline graph using LangGraph."""
    g = StateGraph(DebugState)
    g.add_node("single_agent", single_agent_node)
    g.add_edge(START, "single_agent")
    g.add_edge("single_agent", END)
    return g.compile()
