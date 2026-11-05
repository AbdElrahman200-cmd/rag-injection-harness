from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    customer_id: str
    message: str
    session_id: str = "default"

class DebugInfo(BaseModel):
    chunks: list[dict] = Field(default_factory=list)
    tool_calls: list[dict] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)

class ChatResponse(BaseModel):
    answer: str
    debug: DebugInfo | None = None