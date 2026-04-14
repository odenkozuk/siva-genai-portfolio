"""
Human-in-the-Loop (HITL) Pipeline using LangGraph.
Adds human approval checkpoints for controlled, explainable AI workflows.
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    pending_approval: bool
    approved: bool
    action: str
    result: str


def build_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version="2024-02-01",
        temperature=0,
    )


def analyze_request(state: AgentState) -> AgentState:
    """First node: LLM analyzes the request and proposes an action."""
    llm = build_llm()
    last_message = state["messages"][-1].content
    response = llm.invoke([
        HumanMessage(content=f"""Analyze this request and propose a specific action to take.
Be concise and clear about what you will do.

Request: {last_message}

Proposed Action:""")
    ])
    return {
        **state,
        "messages": [AIMessage(content=response.content)],
        "action": response.content,
        "pending_approval": True,
    }


def human_approval_node(state: AgentState) -> AgentState:
    """HITL checkpoint: prints proposed action and waits for human approval."""
    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Proposed Action:\n{state['action']}")
    print("=" * 60)
    approval = input("Approve this action? (yes/no): ").strip().lower()
    approved = approval in ("yes", "y")
    return {**state, "approved": approved, "pending_approval": False}


def execute_action(state: AgentState) -> AgentState:
    """Execute the approved action."""
    llm = build_llm()
    response = llm.invoke([
        HumanMessage(content=f"Execute the following action and report results:\n{state['action']}")
    ])
    return {
        **state,
        "messages": [AIMessage(content=response.content)],
        "result": response.content,
    }


def reject_action(state: AgentState) -> AgentState:
    """Handle rejected action."""
    rejection_msg = "Action rejected by human reviewer. Please revise your request."
    return {
        **state,
        "messages": [AIMessage(content=rejection_msg)],
        "result": rejection_msg,
    }


def route_after_approval(state: AgentState) -> str:
    return "execute" if state.get("approved") else "reject"


def build_hitl_graph() -> StateGraph:
    memory = MemorySaver()
    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyze_request)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("execute", execute_action)
    graph.add_node("reject", reject_action)

    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "human_approval")
    graph.add_conditional_edges("human_approval", route_after_approval, {
        "execute": "execute",
        "reject": "reject",
    })
    graph.add_edge("execute", END)
    graph.add_edge("reject", END)

    return graph.compile(checkpointer=memory)


def run_hitl(user_request: str, thread_id: str = "default") -> str:
    app = build_hitl_graph()
    config = {"configurable": {"thread_id": thread_id}}
    initial_state: AgentState = {
        "messages": [HumanMessage(content=user_request)],
        "pending_approval": False,
        "approved": False,
        "action": "",
        "result": "",
    }
    final_state = app.invoke(initial_state, config=config)
    return final_state["result"]


if __name__ == "__main__":
    result = run_hitl("Send a notification email to all team members about the Q4 planning meeting on Nov 15.")
    print(f"\nFinal Result: {result}")
