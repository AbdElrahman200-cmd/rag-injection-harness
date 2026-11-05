from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from bot import config, llm, prompt
from bot.schemas import ChatRequest, ChatResponse, DebugInfo

app = FastAPI(title="Reference RAG Support Bot")


# ---- placeholders: Person 2's real functions replace these on Day 2 ----
def _fake_retrieve(query: str, k: int) -> list[dict]:
    return [{
        "doc_id": "refund",
        "text": "Refunds are issued within 14 days of the returned item arriving.",
        "score": 0.0,
        "trusted": True,
    }]


def _fake_customer(customer_id: str) -> dict:
    return {"name": f"Customer {customer_id}", "address": "12 Test St"}
# ------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok", "test_mode": config.TEST_MODE}


@app.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
def chat(req: ChatRequest):
    chunks = _fake_retrieve(req.message, config.TOP_K)
    customer = _fake_customer(req.customer_id)

    if config.USE_STUB:
        answer = f"[stub] You said: {req.message}"
    else:
        system = prompt.load_system(config.HARDEN_PROMPT)
        messages = prompt.build_messages(
            system, chunks, customer, req.message, config.HARDEN_PROMPT
        )
        try:
            answer = llm.ask(messages)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"LLM error: {e}")

    debug = None
    if config.TEST_MODE:
        debug = DebugInfo(chunks=chunks, config=config.as_dict())
    return ChatResponse(answer=answer, debug=debug)