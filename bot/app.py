import json
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from bot import config, llm, prompt, rag, tools
from bot.customers import get_customer
from bot.schemas import ChatRequest, ChatResponse, DebugInfo

app = FastAPI(title="Reference RAG Support Bot")


class PlantRequest(BaseModel):
    doc_id: str = "planted-doc"
    text: str
    trusted: bool = False


def _require_test_mode():
    if not config.TEST_MODE:
        raise HTTPException(status_code=404, detail="Not found")


def _parse_tool_call(text: str) -> dict | None:
    """If the model replied with JSON like {"tool": "get_order_status", "order_id": "1002"},
    return it as a dict. Otherwise return None (it's a normal answer)."""
    m = re.search(r"\{.*?\}", text, re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and data.get("tool") == "get_order_status" and "order_id" in data:
        return data
    return None


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok", "test_mode": config.TEST_MODE}


@app.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
def chat(req: ChatRequest):
    chunks = rag.retrieve(req.message, config.TOP_K)
    customer = get_customer(req.customer_id)
    tool_calls: list[dict] = []

    if config.USE_STUB:
        answer = f"[stub] You said: {req.message}"
    else:
        system = prompt.load_system(config.HARDEN_PROMPT)
        messages = prompt.build_messages(
            system, chunks, customer, req.message, config.HARDEN_PROMPT
        )
        try:
            answer = llm.ask(messages)

            # Tool loop: if the model asked for a tool, run it and give the result back.
            call = _parse_tool_call(answer)
            if call:
                order_id = str(call["order_id"])
                result = tools.get_order_status(order_id, req.customer_id, config.HARDEN_ACCESS)
                tool_calls.append({"tool": call["tool"], "args": {"order_id": order_id}, "result": result})
                messages.append({"role": "assistant", "content": answer})
                messages.append({
                    "role": "user",
                    "content": "Tool result: " + json.dumps(result)
                    + "\n\nUse this result to answer my question. Reply in plain text, not JSON.",
                })
                answer = llm.ask(messages)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"LLM/tool error: {e}")

    debug = None
    if config.TEST_MODE:
        debug = DebugInfo(chunks=chunks, tool_calls=tool_calls, config=config.as_dict())
    return ChatResponse(answer=answer, debug=debug)


@app.post("/test/plant")
def plant(req: PlantRequest):
    _require_test_mode()
    rag.add_document(req.doc_id, req.text, req.trusted)
    return {"status": "planted", "doc_id": req.doc_id}


@app.post("/test/reset")
def reset():
    _require_test_mode()
    rag.reset()
    return {"status": "reset"}