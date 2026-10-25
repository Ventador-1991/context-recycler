"""
CLI entry point for context-recycler.
"""

import argparse
from pathlib import Path
import sys

from context_recycler.smart_context import get_smart_context, ContextRecycler
from context_recycler.counter import count_tokens, TokenGuard


def main():
    parser = argparse.ArgumentParser(
        prog="context-recycler",
        description="Zero-cost local LLM filter, AST tree-shaker, and SHA-256 chunk cache for LLMs."
    )
    parser.add_argument("target", help="File path or code string to condense")
    parser.add_argument("--target-symbol", "-t", type=str, default=None, help="Name of target function/class to preserve fully intact")
    parser.add_argument("--line", "-l", type=int, default=None, help="Line number around which to keep target intact")
    parser.add_argument("--slm", action="store_true", help="Pass through local SLM (Ollama) for dense summarization")
    parser.add_argument("--task", type=str, default="", help="Task goal when using local SLM")
    parser.add_argument("--threshold", type=int, default=4000, help="Warning token threshold (default: 4000)")
    parser.add_argument("--no-cache", action="store_true", help="Disable SHA-256 chunk cache")
    parser.add_argument("--print-code", "-p", action="store_true", help="Print condensed code to stdout")
    parser.add_argument("--output", "-o", type=str, help="Write output to file")

    args = parser.parse_args()

    target_path = Path(args.target)
    if target_path.exists() and target_path.is_file():
        res = get_smart_context(
            file_path=str(target_path),
            target_symbol=args.target_symbol,
            target_line=args.line,
            use_slm=args.slm,
            task_goal=args.task,
            use_cache=not args.no_cache
        )
    else:
        # String processing
        recycler = ContextRecycler(use_cache=not args.no_cache)
        res = recycler.process(
            content=args.target,
            target_symbol=args.target_symbol,
            target_line=args.line,
            use_slm=args.slm,
            task_goal=args.task
        )
        res["file"] = "<raw_input>"

    # Print Report
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    mode_info = res["mode"]
    if res.get("target_found"):
        mode_info += f" (Target Intact: '{args.target_symbol or args.line}')"

    print("\n" + "=" * 76)
    print(f"{BOLD}{CYAN}♻️  CONTEXT RECYCLER REPORT{RESET}")
    print("=" * 76)
    print(f"  • Source:           {BOLD}{res.get('file', 'N/A')}{RESET}")
    print(f"  • Active Mode:      {mode_info}")
    print(f"  • Raw Tokens:       {YELLOW}{res['orig_tokens']:,}{RESET} tokens")
    print(f"  • Condensed Tokens: {GREEN}{res['condensed_tokens']:,}{RESET} tokens")
    print(f"  • Tokens Saved:     {BOLD}{GREEN}-{res['saved_tokens']:,}{RESET} tokens ({BOLD}{res['pct_saved']}% reduction{RESET})")
    print(f"  • Cache Hit:        {'✅ True (0ms)' if res.get('cache_hit') else '❌ False'}")
    print("=" * 76 + "\n")

    if args.print_code:
        print(res["code"])

    if args.output:
        out_f = Path(args.output).resolve()
        out_f.parent.mkdir(parents=True, exist_ok=True)
        out_f.write_text(res["code"], encoding="utf-8")
        print(f"✓ Saved condensed context to: {out_f}")


if __name__ == "__main__":
    main()
