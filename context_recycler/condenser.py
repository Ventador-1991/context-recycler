"""
Deterministic Code Minifier and Comment Stripper for Multi-Language Source Code.
"""

from pathlib import Path
import re


def detect_language(path_or_filename: str) -> str:
    ext = Path(path_or_filename).suffix.lower()
    mapping = {
        ".py": "python",
        ".rs": "rust",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "css",
        ".sql": "sql",
        ".sh": "bash",
        ".bash": "bash",
        ".go": "go",
        ".c": "c",
        ".cpp": "cpp",
        ".java": "java"
    }
    return mapping.get(ext, "python")


def strip_comments(code: str, lang: str = "python") -> str:
    """
    Strips non-essential comments while preserving shebangs, directives, and syntax integrity.
    """
    lang = lang.lower()

    if lang in ["python", "py"]:
        lines = []
        for line in code.splitlines():
            if line.startswith("#!") or "coding:" in line or "# type:" in line:
                lines.append(line)
                continue
            stripped = re.sub(r'#.*$', '', line)
            if stripped.strip() or line.strip() == "":
                lines.append(stripped)
        return "\n".join(lines)

    elif lang in ["rust", "rs", "javascript", "js", "typescript", "ts", "c", "cpp", "go", "java", "css"]:
        no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        lines = []
        for line in no_block.splitlines():
            stripped = re.sub(r'//.*$', '', line)
            lines.append(stripped)
        return "\n".join(lines)

    elif lang in ["html", "htm", "xml"]:
        return re.sub(r'<!--.*?-->', '', code, flags=re.DOTALL)

    elif lang in ["sql"]:
        no_block = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return re.sub(r'--.*$', '', no_block, flags=re.MULTILINE)

    return code


def minify_whitespace(code: str, lang: str = "python") -> str:
    """
    Collapses redundant blank lines and trailing whitespace while preserving semantic indentation.
    """
    lines = code.splitlines()
    cleaned = []
    prev_blank = False

    for line in lines:
        r_stripped = line.rstrip()
        is_blank = (len(r_stripped.strip()) == 0)

        if is_blank:
            if not prev_blank:
                cleaned.append("")
                prev_blank = True
        else:
            cleaned.append(r_stripped)
            prev_blank = False

    return "\n".join(cleaned).strip()
