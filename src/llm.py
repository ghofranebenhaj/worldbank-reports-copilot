import requests
from src import config

SYSTEM_PROMPT = (
    "You answer questions about World Bank reports using ONLY the provided context. "
    "Cite sources as [document, p.X]. "
    "If the context does not contain the answer, reply exactly: "
    "I don't know based on the provided documents."
)


def generate(question, passages):
    context = "\n\n".join(
        f"[{p['document']}, p.{p['page']}]\n{p['content']}" for p in passages
    )
    user = f"Context:\n{context}\n\nQuestion: {question}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
    if config.LLM_PROVIDER == "openai":
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
            json={"model": config.OPENAI_MODEL, "temperature": 0, "messages": messages},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    r = requests.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={
            "model": config.OLLAMA_MODEL,
            "stream": False,
            "options": {"temperature": 0},
            "messages": messages,
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]
