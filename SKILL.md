---
name: context-recycler
description: >-
  Zero-cost local LLM filter, AST tree-shaker, and SHA-256 semantic chunk cache for AI coding agents.
  Reduces token consumption by 65% to 85% on large context files, eliminates hallucinations with
  Focused Edit Mode, and recycles unchanged blocks instantly.
---

# Context Recycler (AI Agent Skill)

Use this skill whenever you need to inspect or supply large source code files to your context window without burning token quotas.

## When to Activate This Skill
- Reading large dependency files (> 200 lines) to understand class signatures, functions, or imports.
- Performing targeted modifications on a function without injecting hundreds of lines of unrelated sibling code.
- Checking token budget or protecting context from exceeding 4,000 tokens.

## How to Execute

### 1. Architectural Mode (Whole File Skeletonization)
When you need to know what a file exports or how its classes are structured:
```bash
context-recycler <path/to/file>
```
*Saves 75% to 85% of input tokens by replacing function bodies with `...`.*

### 2. Focused Edit Mode (Zero Hallucination Modification)
When you need to edit or inspect a specific function or class inside a large file:
```bash
context-recycler <path/to/file> --target-symbol <function_or_class_name> --print-code
```
*Keeps the target function 100% INTACT with full implementation and comments, while skeletonizing all other methods.*

### 3. Local SLM Dense Summarization (Offline via Ollama)
When dealing with massive unstructured text, error traces, or complex logic:
```bash
context-recycler <path/to/file> --slm --task "<task_goal>"
```
*Pipes through local Qwen 2.5 Coder or Llama 3.2 at zero cloud cost.*
