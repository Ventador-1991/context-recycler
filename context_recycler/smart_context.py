"""
Smart Context Recycler Orchestrator: Dual-Mode Focused Condensation.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from context_recycler.counter import count_tokens
from context_recycler.condenser import strip_comments, minify_whitespace, detect_language
from context_recycler.tree_shaker import smart_tree_shake_python, tree_shake_rust
from context_recycler.cache import SemanticChunkCache
from context_recycler.slm_recycler import compress_with_local_slm


class ContextRecycler:
    """
    Main orchestrator for Context Recycler.
    """

    def __init__(self, use_cache: bool = True):
        self.cache = SemanticChunkCache() if use_cache else None

    def process(
        self,
        content: str,
        lang: str = "python",
        target_symbol: Optional[str] = None,
        target_line: Optional[int] = None,
        use_slm: bool = False,
        task_goal: str = ""
    ) -> Dict[str, Any]:
        orig_tokens = count_tokens(content)

        # 1. Cache Lookup (if not using dynamic target or SLM)
        if self.cache and not target_symbol and not target_line and not use_slm:
            cached_text, hit = self.cache.lookup(content)
            if hit and cached_text:
                condensed_tokens = count_tokens(cached_text)
                return {
                    "code": cached_text,
                    "orig_tokens": orig_tokens,
                    "condensed_tokens": condensed_tokens,
                    "saved_tokens": orig_tokens - condensed_tokens,
                    "pct_saved": round((orig_tokens - condensed_tokens) / orig_tokens * 100.0, 1) if orig_tokens > 0 else 0,
                    "cache_hit": True,
                    "mode": "cache_lookup"
                }

        target_found = False
        mode = "architectural_skeleton"

        # 2. Dual-Mode AST Tree-Shaking
        if target_symbol or target_line:
            mode = "focused_edit_mode"
            if lang in ["python", "py"]:
                condensed, target_found = smart_tree_shake_python(content, target_symbol=target_symbol, target_line=target_line)
            elif lang in ["rust", "rs"]:
                condensed, target_found = tree_shake_rust(content, target_symbol=target_symbol)
            else:
                condensed = content
        else:
            if lang in ["python", "py"]:
                condensed, _ = smart_tree_shake_python(content)
            elif lang in ["rust", "rs"]:
                condensed, _ = tree_shake_rust(content)
            else:
                condensed = strip_comments(content, lang=lang)

        # 3. Minification
        condensed = minify_whitespace(condensed, lang=lang)

        # 4. Optional Local SLM Pass
        if use_slm:
            slm_res = compress_with_local_slm(condensed, task_goal=task_goal)
            if slm_res:
                condensed = slm_res
                mode += "+local_slm"

        condensed_tokens = count_tokens(condensed)
        saved_tokens = max(0, orig_tokens - condensed_tokens)
        pct_saved = round((saved_tokens / orig_tokens * 100.0), 1) if orig_tokens > 0 else 0.0

        # Store in cache if general architectural representation
        if self.cache and not target_symbol and not target_line and not use_slm:
            self.cache.store(content, condensed, orig_tokens, condensed_tokens)

        return {
            "code": condensed,
            "orig_tokens": orig_tokens,
            "condensed_tokens": condensed_tokens,
            "saved_tokens": saved_tokens,
            "pct_saved": pct_saved,
            "cache_hit": False,
            "mode": mode,
            "target_found": target_found
        }


def get_smart_context(
    file_path: str,
    target_symbol: Optional[str] = None,
    target_line: Optional[int] = None,
    use_slm: bool = False,
    task_goal: str = "",
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to optimize a file path with smart context recycling.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    raw_text = path.read_text(encoding="utf-8")
    lang = detect_language(str(path))
    recycler = ContextRecycler(use_cache=use_cache)
    res = recycler.process(
        content=raw_text,
        lang=lang,
        target_symbol=target_symbol,
        target_line=target_line,
        use_slm=use_slm,
        task_goal=task_goal
    )
    res["file"] = str(path)
    res["lang"] = lang
    return res
