"""
LangChain Middleware Pipeline — agent-tool integration with custom callbacks.
Implements controllable, observable AI workflow middleware.
"""

import os
from typing import Any
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import tool
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()


class AuditCallbackHandler(BaseCallbackHandler):
    """Logs all LLM calls and tool uses for audit and compliance tracking."""

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        print(f"[AUDIT] LLM call started. Model: {serialized.get('name', 'unknown')}")

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        print(f"[AUDIT] Tool called: {serialized.get('name')} | Input: {input_str[:100]}")

    def on_tool_end(self, output: str, **kwargs):
        print(f"[AUDIT] Tool result: {output[:100]}")

    def on_llm_end(self, response, **kwargs):
        usage = getattr(response, "llm_output", {})
        print(f"[AUDIT] LLM call complete. Token usage: {usage.get('token_usage', 'N/A')}")


@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for information."""
    kb = {
        "leave policy": "Employees are entitled to 18 days of paid leave per year.",
        "expense policy": "Expenses above $500 require manager approval. Submit within 30 days.",
        "remote work": "Remote work is allowed up to 3 days per week with manager approval.",
    }
    for key, value in kb.items():
        if key in query.lower():
            return value
    return "No matching policy found. Please contact HR for more information."


@tool
def create_ticket(description: str) -> str:
    """Create a support ticket for the given issue description."""
    import uuid
    ticket_id = f"TKT-{str(uuid.uuid4())[:6].upper()}"
    return f"Ticket {ticket_id} created successfully. Expected resolution: 2 business days."


def build_middleware_agent() -> AgentExecutor:
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version="2024-02-01",
        temperature=0,
    )
    tools = [search_knowledge_base, create_ticket]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an enterprise AI assistant. Use the available tools to help employees."),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[AuditCallbackHandler()],
        verbose=True,
        max_iterations=5,
    )


def run_agent(query: str) -> str:
    executor = build_middleware_agent()
    result = executor.invoke({"input": query})
    return result["output"]


if __name__ == "__main__":
    response = run_agent("What is the company's remote work policy?")
    print(f"\nResponse: {response}")
