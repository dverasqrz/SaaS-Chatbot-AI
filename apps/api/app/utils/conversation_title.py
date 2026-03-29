from __future__ import annotations

import re


def suggest_conversation_title(user_text: str, max_words: int = 3, max_len: int = 80) -> str:
    """
    Gera um título curto (2–3 palavras) a partir da primeira mensagem do utilizador.
    """
    if not user_text or not user_text.strip():
        return "Nova conversa"

    cleaned = re.sub(r"[^\w\s\u00C0-\u024F]", " ", user_text, flags=re.UNICODE)
    words = [w for w in cleaned.split() if len(w) > 1][:max_words]
    if not words:
        return "Nova conversa"

    title = " ".join(words).strip()
    if len(title) > max_len:
        title = title[:max_len].rsplit(" ", 1)[0]

    return title[0].upper() + title[1:] if title else "Nova conversa"
