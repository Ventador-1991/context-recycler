"""
Zero-Cost Local SLM Recycler using Ollama (qwen2.5-coder, llama3.2, etc.).
"""

import json
import os
from typing import Optional, Tuple, List
import urllib.request

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://127.0.0.1:11434")


def check_ollama_status() -> Tuple[bool, List[str]]:
    """
    Checks if Ollama daemon is running locally and retrieves available models.
    """
    try:
        req = urllib.request.Request(f"{OLLAMA_API_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models
    except Exception:
        return False, []


def compress_with_local_slm(
    text: str,
    task_goal: str = "",
    model: Optional[str] = None,
    timeout: float = 45.0
) -> Optional[str]:
    """
    Passes raw code or documentation to local SLM (e.g., Qwen 2.5 Coder 1.5B or Llama 3.2)
    via Ollama to extract ultra-dense, token-minified representation at ZERO cloud cost.
    """
    avail, models = check_ollama_status()
    if not avail:
        return None

    selected_model = model
    if not selected_model:
        if "qwen2.5-coder:1.5b" in models:
            selected_model = "qwen2.5-coder:1.5b"
        elif "llama3.2:latest" in models or "llama3.2" in models:
            selected_model = "llama3.2:latest"
        elif "qwen2.5-coder:3b" in models:
            selected_model = "qwen2.5-coder:3b"
        elif models:
            selected_model = models[0]
        else:
            return None

    system_instruction = (
        "You are an ultra-fast code and context condenser. Your job is to extract ONLY the essential logic, "
        "function signatures, data structures, and context required for the user's task. "
        "Remove all boilerplate, obvious comments, and unrelated code. "
        "Output an ultra-dense, token-minified representation that an LLM can immediately understand. "
        "Do not explain your changes; output ONLY the condensed content."
    )

    user_prompt = f"Goal/Task: {task_goal if task_goal else 'Extract essential logic and structure'}\n\nContext:\n{text[:3500]}"

    payload = {
        "model": selected_model,
        "prompt": f"{system_instruction}\n\n{user_prompt}",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 256,
            "num_ctx": 2048
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_API_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            res_obj = json.loads(resp.read().decode("utf-8"))
            condensed = res_obj.get("response", "").strip()
            if condensed:
                return condensed
    except Exception:
        pass

    return None
