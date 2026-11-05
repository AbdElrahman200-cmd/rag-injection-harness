import os
from dotenv import load_dotenv

load_dotenv()

def _flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default) == "1"

MODEL = os.getenv("MODEL", "ollama/llama3.2:3b")
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
TOP_K = int(os.getenv("TOP_K", "3"))
TEST_MODE = _flag("TEST_MODE")
USE_STUB = _flag("USE_STUB")
HARDEN_PROMPT = _flag("HARDEN_PROMPT")
HARDEN_ACCESS = _flag("HARDEN_ACCESS")
HARDEN_OUTPUT = _flag("HARDEN_OUTPUT")

def as_dict() -> dict:
    return {
        "model": MODEL, "temperature": TEMPERATURE, "top_k": TOP_K,
        "harden_prompt": HARDEN_PROMPT, "harden_access": HARDEN_ACCESS,
        "harden_output": HARDEN_OUTPUT,
    }