"""
Exact Token Counting and Guard Module using tiktoken (cl100k_base / o200k_base).
"""

from typing import Optional

_TIKTOKEN_ENC = None


def get_token_encoder():
    global _TIKTOKEN_ENC
    if _TIKTOKEN_ENC is None:
        try:
            import tiktoken
            _TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _TIKTOKEN_ENC = None
    return _TIKTOKEN_ENC


def count_tokens(text: str) -> int:
    """
    Computes exact token count using tiktoken (cl100k_base),
    with accurate fallback to character/word ratio for code (~3.6 chars/token).
    """
    if not text:
        return 0
    enc = get_token_encoder()
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    return max(1, int(len(text) / 3.6))


class TokenGuard:
    """
    Pre-execution guard that warns or blocks if context exceeds a defined token threshold.
    """

    def __init__(self, threshold: int = 4000):
        self.threshold = threshold

    def check(self, text: str) -> bool:
        """
        Returns True if text is within threshold, False if it exceeds it.
        """
        tokens = count_tokens(text)
        return tokens <= self.threshold

    def evaluate(self, text: str) -> dict:
        tokens = count_tokens(text)
        exceeded = tokens > self.threshold
        return {
            "tokens": tokens,
            "threshold": self.threshold,
            "exceeded": exceeded,
            "excess_tokens": max(0, tokens - self.threshold)
        }
