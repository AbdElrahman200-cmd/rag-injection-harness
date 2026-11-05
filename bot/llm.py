from litellm import completion
from bot import config

def ask(messages: list[dict]) -> str:
    resp = completion(
        model=config.MODEL,
        messages=messages,
        api_base=config.OLLAMA_BASE,
        temperature=config.TEMPERATURE,
    )
    return resp.choices[0].message.content