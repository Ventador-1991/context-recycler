"""
Unit Tests for Context Recycler.
"""

from context_recycler.counter import count_tokens, TokenGuard
from context_recycler.condenser import strip_comments, minify_whitespace
from context_recycler.tree_shaker import smart_tree_shake_python
from context_recycler.smart_context import ContextRecycler


def test_token_counter():
    text = "def hello():\n    return 'world'"
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_strip_comments():
    code = "# This is a comment\nx = 10  # inline\n"
    res = strip_comments(code, "python")
    assert "This is a comment" not in res
    assert "x = 10" in res


def test_smart_tree_shake_intact_target():
    sample_code = """
import os

def helper_one():
    a = 1
    b = 2
    return a + b

def target_func(x: int) -> int:
    # Important logic
    return x * 42

def helper_two():
    return 'unused'
"""
    condensed, found = smart_tree_shake_python(sample_code, target_symbol="target_func")
    assert found is True
    assert "def helper_one(): ..." in condensed or "def helper_one():\n    ..." in condensed
    assert "return x * 42" in condensed  # Target logic is 100% intact!
    assert "def helper_two(): ..." in condensed or "def helper_two():\n    ..." in condensed


def test_context_recycler_cache():
    code = "def sample(): return 123"
    recycler = ContextRecycler(use_cache=True)
    res1 = recycler.process(code, lang="python")
    assert res1["cache_hit"] is False

    res2 = recycler.process(code, lang="python")
    assert res2["cache_hit"] is True
    assert res2["condensed_tokens"] == res1["condensed_tokens"]


if __name__ == "__main__":
    test_token_counter()
    test_strip_comments()
    test_smart_tree_shake_intact_target()
    test_context_recycler_cache()
    print("All unit tests passed successfully!")
