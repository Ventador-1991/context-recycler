"""
Context Recycler: Zero-cost local LLM filter, AST tree-shaker, and SHA-256 chunk cache for LLMs.
"""

from context_recycler.counter import count_tokens, TokenGuard
from context_recycler.condenser import strip_comments, minify_whitespace, detect_language
from context_recycler.tree_shaker import tree_shake_python, tree_shake_rust, smart_tree_shake_python
from context_recycler.cache import SemanticChunkCache
from context_recycler.slm_recycler import compress_with_local_slm, check_ollama_status
from context_recycler.smart_context import get_smart_context, ContextRecycler

__version__ = "1.0.0"
__all__ = [
    "count_tokens",
    "TokenGuard",
    "strip_comments",
    "minify_whitespace",
    "detect_language",
    "tree_shake_python",
    "tree_shake_rust",
    "smart_tree_shake_python",
    "SemanticChunkCache",
    "compress_with_local_slm",
    "check_ollama_status",
    "get_smart_context",
    "ContextRecycler"
]
