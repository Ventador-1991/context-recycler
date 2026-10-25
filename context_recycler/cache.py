"""
Semantic Chunk Buffer and SHA-256 Hash Cache for Repeated Context Recycling.
"""

import hashlib
import json
import os
from pathlib import Path
import time
from typing import Dict, Any, Tuple, Optional

DEFAULT_CACHE_DIR = Path(os.environ.get("CONTEXT_RECYCLER_CACHE", Path.home() / ".cache" / "context-recycler"))


class SemanticChunkCache:
    """
    Caches condensed code representations by SHA-256 hash.
    If the file or function chunk has not changed, retrieves it in 0ms without re-processing.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "chunk_cache.json"
        self.cache: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_cache(self):
        try:
            self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def lookup(self, content: str) -> Tuple[Optional[str], bool]:
        """
        Looks up content hash. Returns (condensed_text, hit).
        """
        ch_hash = self.compute_hash(content)
        if ch_hash in self.cache:
            entry = self.cache[ch_hash]
            entry["last_accessed"] = time.time()
            entry["hits"] = entry.get("hits", 0) + 1
            return entry.get("condensed"), True
        return None, False

    def store(self, content: str, condensed: str, orig_tokens: int, condensed_tokens: int):
        ch_hash = self.compute_hash(content)
        self.cache[ch_hash] = {
            "hash": ch_hash,
            "orig_tokens": orig_tokens,
            "condensed_tokens": condensed_tokens,
            "condensed": condensed,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "hits": 0
        }
        if len(self.cache) > 1000:
            oldest = sorted(self.cache.keys(), key=lambda k: self.cache[k].get("last_accessed", 0))[:100]
            for k in oldest:
                del self.cache[k]
        self._save_cache()
