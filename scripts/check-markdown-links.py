#!/usr/bin/env python3
"""check-markdown-links.py — Markdown 相对链接只读检查器

扫描 ROOT 下所有 *.md 文件，校验内联 ``[text](target)`` 形式的相对链接：

- 跳过协议链接（http://、https://、mailto:、ftp://）
- 跳过纯锚点（#section）
- 跳过整体被 ``<...>`` 包裹的占位符（如 ``<app-dir>``）
- template 模式额外跳过以 ``...`` 结尾或包含 ``<...>`` 子串的目标
- 跳过 ```` ``` ```` 围栏内的整段代码块
- 从 target 中剥离 URL fragment（``#anchor``）与可选 title（``"title"`` / ``'title'``）
- 相对路径从 Markdown 文件父目录出发，验证文件或目录是否存在

输出: 每个断链打印一行 ``file:line  ->  target``（行号 1-indexed）。
退出码: 无断链 = 0；存在断链 = 1；参数错误 = 2。

仅使用 Python 3 标准库；零第三方依赖；只读（不修改任何文件）。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

# 内联链接 [text](target) —— target 内部不含未转义 )
# （未处理 \[ \] \) 转义；与本仓库实际文档匹配）
INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")

# 围栏: 行首可选空白 + 3 个及以上同字符（` 或 ~），仅做粗略识别
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

# 协议前缀（lstrip 后比较）
PROTOCOL_PREFIXES = ("http://", "https://", "mailto:", "ftp://")

# 模板占位符: 任意 <...> 子串
TEMPLATE_PLACEHOLDER_RE = re.compile(r"<[^>\s]+>")

# 尾部可选 title: target 后接空白 + 引号串；引号可双可单
TRAILING_TITLE_RE = re.compile(r"\s+['\"][^'\"]*['\"]\s*$")


def strip_title_and_fragment(target: str) -> str:
    """从 target 中剥离尾部可选 title 与 fragment（#anchor），并解 URL 编码。"""
    t = target.strip()
    t = TRAILING_TITLE_RE.sub("", t)
    if "#" in t:
        t = t.split("#", 1)[0]
    t = t.strip()
    try:
        from urllib.parse import unquote

        t = unquote(t)
    except Exception:
        # 编码不合法时保留原值，避免检查器本身崩溃
        pass
    return t


def is_placeholder_target(target: str) -> bool:
    """target 整体被 ``<...>`` 包裹 → 占位符，直接跳过。"""
    t = target.strip()
    return len(t) >= 2 and t.startswith("<") and t.endswith(">")


def is_template_target(target: str) -> bool:
    """template 模式额外跳过的目标: 以 ``...`` 结尾或包含 ``<...>`` 子串。"""
    t = target.strip()
    if t.endswith("..."):
        return True
    if TEMPLATE_PLACEHOLDER_RE.search(t):
        return True
    return False


def starts_with_protocol(target: str) -> bool:
    return target.lstrip().startswith(PROTOCOL_PREFIXES)


def is_pure_anchor(target: str) -> bool:
    return target.lstrip().startswith("#")


def extract_links(line: str) -> Iterable[Tuple[str, str]]:
    """从一行提取所有 (text, target-cleaned)，target 已剥离 title/fragment。"""
    for m in INLINE_LINK_RE.finditer(line):
        text = m.group(1)
        target = strip_title_and_fragment(m.group(2))
        yield text, target


def check_file(
    md_path: Path, root: Path, template_mode: bool
) -> List[Tuple[Path, int, str]]:
    """检查单个 .md 文件，返回断链列表 [(relative_path, line_no, raw_target), ...]。"""
    broken: List[Tuple[Path, int, str]] = []
    try:
        content = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return broken

    in_code_block = False
    fence_marker: str | None = None

    try:
        rel_md = md_path.relative_to(root)
    except ValueError:
        rel_md = md_path

    for line_no, line in enumerate(content.splitlines(), start=1):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_code_block:
                in_code_block = True
                fence_marker = marker
                continue
            # 闭合: 围栏字符类与长度 ≥ 开启围栏
            if marker[0] == (fence_marker or "")[0] and len(marker) >= len(
                fence_marker or ""
            ):
                in_code_block = False
                fence_marker = None
            continue
        if in_code_block:
            continue

        for _text, target in extract_links(line):
            if not target:
                continue
            if is_placeholder_target(target):
                continue
            if template_mode and is_template_target(target):
                continue
            if starts_with_protocol(target):
                continue
            if is_pure_anchor(target):
                continue

            clean = target[2:] if target.startswith("./") else target
            candidate = Path(os.path.normpath(os.path.join(str(md_path.parent), clean)))
            if not candidate.exists():
                broken.append((rel_md, line_no, target))

    return broken


def iter_md_files(root: Path) -> Iterable[Path]:
    """遍历 root 下所有 .md 文件（跳过以 . 开头的目录，如 .git / .worktrees）。"""
    for path in root.rglob("*.md"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part.startswith(".") for part in rel.parts):
            continue
        yield path


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Markdown 相对链接只读检查器（仅标准库）。"
    )
    parser.add_argument("--root", default=".", help="扫描根目录（默认 .）")
    parser.add_argument(
        "--template",
        action="store_true",
        help="启用模板占位符跳过模式（额外跳过 ... 结尾 / 含 <…> 的 target）",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root 不是目录: {root}", file=sys.stderr)
        return 2

    all_broken: List[Tuple[Path, int, str]] = []
    for md_path in iter_md_files(root):
        all_broken.extend(check_file(md_path, root, args.template))

    for rel_md, line_no, target in all_broken:
        print(f"{rel_md}:{line_no}  ->  {target}")

    return 1 if all_broken else 0


if __name__ == "__main__":
    sys.exit(main())