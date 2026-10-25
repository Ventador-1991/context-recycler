"""
AST Tree-Shaker for Python and Regex-based Skeletonizer for Rust & Other Languages.
"""

import ast
import re
from typing import Optional, Tuple


def tree_shake_python(code: str) -> str:
    """
    Extracts module imports, constants, classes, and function signatures.
    Replaces function bodies with '...' (Ellipsis), yielding 75%-85% token reduction.
    """
    res, _ = smart_tree_shake_python(code, target_symbol=None, target_line=None)
    return res


def smart_tree_shake_python(
    code: str,
    target_symbol: Optional[str] = None,
    target_line: Optional[int] = None
) -> Tuple[str, bool]:
    """
    Selective Tree-Shaking in Python:
    If 'target_symbol' or 'target_line' is specified, preserves the target function/class
    100% INTACT with full implementation body, while skeletonizing all sibling functions.
    Returns (shaken_code, target_found).
    """
    try:
        tree = ast.parse(code)
    except Exception:
        return code, False

    shaken_lines = []
    target_found = False

    for node in tree.body:
        # 1. Imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            shaken_lines.append(ast.unparse(node))

        # 2. Module Constants
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and (target.id.isupper() or target.id.endswith("_CONFIG") or target.id.endswith("_DIR") or target.id.endswith("_MAP")):
                    shaken_lines.append(ast.unparse(node))
                    break

        # 3. Class Definitions
        elif isinstance(node, ast.ClassDef):
            is_class_target = (target_symbol and node.name == target_symbol)
            if not is_class_target and target_line and hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.lineno <= target_line <= node.end_lineno:
                    is_class_target = True

            if is_class_target:
                shaken_lines.append(f"# [TARGET ENTIRE CLASS INTACT: {node.name}]\n" + ast.unparse(node))
                target_found = True
            else:
                class_str = f"class {node.name}"
                if node.bases:
                    bases_str = ", ".join(ast.unparse(b) for b in node.bases)
                    class_str += f"({bases_str})"
                class_str += ":"

                class_body_lines = []
                doc = ast.get_docstring(node)
                if doc:
                    class_body_lines.append(f'    """{doc[:120]}..."""')

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        is_method_target = (target_symbol and item.name == target_symbol)
                        if not is_method_target and target_line and hasattr(item, "lineno") and hasattr(item, "end_lineno"):
                            if item.lineno <= target_line <= item.end_lineno:
                                is_method_target = True

                        if is_method_target:
                            full_method = ast.unparse(item)
                            indented_method = "\n".join("    " + l for l in full_method.splitlines())
                            class_body_lines.append(f"    # [TARGET METHOD INTACT: {item.name}]\n" + indented_method)
                            target_found = True
                        else:
                            prefix = "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                            args = ast.unparse(item.args)
                            ret = f" -> {ast.unparse(item.returns)}" if item.returns else ""
                            class_body_lines.append(f"    {prefix} {item.name}({args}){ret}: ...")
                    elif isinstance(item, ast.Assign):
                        class_body_lines.append(f"    {ast.unparse(item)}")

                if not class_body_lines:
                    class_body_lines.append("    ...")
                shaken_lines.append(class_str + "\n" + "\n".join(class_body_lines))

        # 4. Top-level Functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_fn_target = (target_symbol and node.name == target_symbol)
            if not is_fn_target and target_line and hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.lineno <= target_line <= node.end_lineno:
                    is_fn_target = True

            if is_fn_target:
                shaken_lines.append(f"# ========================================================\n"
                                    f"# [TARGET FUNCTION INTACT: {node.name}] (EDIT TARGET)\n"
                                    f"# ========================================================\n"
                                    + ast.unparse(node))
                target_found = True
            else:
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                args = ast.unparse(node.args)
                ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
                doc = ast.get_docstring(node)
                fn_body = f'    """{doc[:80]}..."""\n    ...' if doc else "    ..."
                shaken_lines.append(f"{prefix} {node.name}({args}){ret}:\n{fn_body}")

    return "\n\n".join(shaken_lines), target_found


def tree_shake_rust(code: str, target_symbol: Optional[str] = None) -> Tuple[str, bool]:
    """
    Extracts public structs, traits, and function signatures in Rust without function bodies,
    preserving target_symbol block intact if supplied.
    """
    lines = code.splitlines()
    output_lines = []
    target_found = False
    in_target_block = False
    target_brace_depth = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("use ") and stripped.endswith(";"):
            output_lines.append(stripped)
            continue

        if target_symbol and not in_target_block:
            if re.search(rf'\b(fn|struct|enum|trait|impl)\s+{target_symbol}\b', stripped):
                in_target_block = True
                target_found = True
                target_brace_depth = stripped.count("{") - stripped.count("}")
                output_lines.append(f"\n// [TARGET INTACT: {target_symbol}]")
                output_lines.append(line)
                if target_brace_depth <= 0 and "{" in stripped:
                    in_target_block = False
                continue

        if in_target_block:
            output_lines.append(line)
            target_brace_depth += stripped.count("{") - stripped.count("}")
            if target_brace_depth <= 0:
                in_target_block = False
            continue

        if re.match(r'^(pub\s+)?(struct|enum|type|const|static)\s+', stripped):
            output_lines.append(stripped)
            continue

        if re.match(r'^(pub(\(.*?\))?\s+)?(async\s+)?fn\s+', stripped):
            sig = stripped.split("{")[0].strip() + " { ... }"
            output_lines.append(sig)
            continue

    return "\n".join(output_lines), target_found
