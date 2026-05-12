from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Ensure the module directory is on the path when running from a different cwd
sys.path.insert(0, os.path.dirname(__file__))

import agent_service

app = FastAPI(title="Todo Agent API")

# Allow the React dev server (and any local origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Accepts a free-text message from the client and returns the agent'\''s reply.
    """
    reply = agent_service.agent(request.message)
    return ChatResponse(reply=reply)


@app.get("/")
def root():
    return {"status": "ok", "message": "Todo Agent API is running"}
