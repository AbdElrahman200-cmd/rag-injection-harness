from pathlib import Path

PROMPTS = Path(__file__).parent / "prompts"

def load_system(harden: bool) -> str:
    name = "system_hardened.txt" if harden else "system.txt"
    path = PROMPTS / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "You are a helpful customer support assistant."

def build_messages(system: str, chunks: list[dict], customer: dict,
                   user_msg: str, harden: bool) -> list[dict]:
    context = "\n\n".join(c["text"] for c in chunks)
    customer_block = "\n".join(f"{k}: {v}" for k, v in customer.items())
    if harden:
        context = f"<retrieved_documents>\n{context}\n</retrieved_documents>"

    content = (
        f"{system}\n\n"
        f"Knowledge base excerpts:\n{context}\n\n"
        f"Current customer record:\n{customer_block}"
    )
    return [
        {"role": "system", "content": content},
        {"role": "user", "content": user_msg},
    ]