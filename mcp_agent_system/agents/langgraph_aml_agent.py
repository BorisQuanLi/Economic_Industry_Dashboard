"""
LangGraph AML risk assessment agent.
StateGraph: ingest → retrieve → reason → (escalate | respond)
"""
import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a Wells Fargo AML compliance analyst. "
    "Given sector data, assess AML risk and explain your reasoning concisely."
)

HIGH_RISK_FLAG = "High Capacity / Review Needed"


class AMLAgentState(TypedDict):
    query: str
    retrieved_context: str
    aml_risk_flag: str
    response: str


def build_aml_graph(retriever, llm):
    """Factory: inject retriever and llm so they can be mocked in tests."""

    def ingest(state: AMLAgentState) -> AMLAgentState:
        return {**state, "retrieved_context": "", "aml_risk_flag": "", "response": ""}

    def retrieve(state: AMLAgentState) -> AMLAgentState:
        docs = retriever.invoke(state["query"])
        top = docs[0] if docs else None
        context = top.page_content if top else "No data available."
        flag = top.metadata.get("aml_risk_flag", "") if top else ""
        return {**state, "retrieved_context": context, "aml_risk_flag": flag}

    def reason(state: AMLAgentState) -> AMLAgentState:
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Query: {state['query']}\nContext: {state['retrieved_context']}"),
        ]
        result = llm.invoke(messages)
        return {**state, "response": result.content}

    def respond(state: AMLAgentState) -> AMLAgentState:
        return state

    def escalate(state: AMLAgentState) -> AMLAgentState:
        logger.warning("AML escalation triggered for query: %s", state["query"])
        return {**state, "response": f"[ESCALATED] {state['response']}"}

    def _route(state: AMLAgentState) -> str:
        return "escalate" if state["aml_risk_flag"] == HIGH_RISK_FLAG else "respond"

    graph = StateGraph(AMLAgentState)
    for name, fn in [("ingest", ingest), ("retrieve", retrieve), ("reason", reason),
                     ("respond", respond), ("escalate", escalate)]:
        graph.add_node(name, fn)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "retrieve")
    graph.add_edge("retrieve", "reason")
    graph.add_conditional_edges("reason", _route, {"escalate": "escalate", "respond": "respond"})
    graph.add_edge("escalate", END)
    graph.add_edge("respond", END)

    return graph.compile()
