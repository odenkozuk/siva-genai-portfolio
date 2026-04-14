"""
FastAPI microservice for AI request processing on Azure Kubernetes Service (AKS).
Handles 100K+ daily requests with event-driven Azure Queue integration.
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from azure.storage.queue import QueueClient
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

app = FastAPI(title="AI Microservice", version="1.0.0")


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    metadata: dict = {}


class ChatResponse(BaseModel):
    session_id: str
    response: str
    tokens_used: int = 0


def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        api_version="2024-02-01",
        temperature=0,
    )


def get_queue_client() -> QueueClient:
    return QueueClient.from_connection_string(
        conn_str=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        queue_name=os.getenv("AZURE_QUEUE_NAME", "ai-requests"),
    )


async def process_queue_message(message_body: dict) -> None:
    """Background task: process a message from the Azure Queue."""
    llm = get_llm()
    response = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: llm.invoke([HumanMessage(content=message_body.get("message", ""))]),
    )
    print(f"[Queue] Processed session {message_body.get('session_id')}: {response.content[:50]}...")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-microservice"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=request.message)])
        background_tasks.add_task(
            log_to_queue,
            session_id=request.session_id,
            message=request.message,
            response=response.content,
        )
        return ChatResponse(
            session_id=request.session_id,
            response=response.content,
            tokens_used=response.usage_metadata.get("total_tokens", 0) if response.usage_metadata else 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def log_to_queue(session_id: str, message: str, response: str) -> None:
    """Log request/response to Azure Queue for downstream processing."""
    try:
        queue_client = get_queue_client()
        payload = json.dumps({"session_id": session_id, "message": message[:200], "response": response[:200]})
        queue_client.send_message(payload)
    except Exception as e:
        print(f"[Queue] Failed to log: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
