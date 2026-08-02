#!/usr/bin/env python3
"""check-governance-consistency.py — Governance 关键规则一致性检查器

仅做模式匹配 + 块级豁免（`> **已取代**` 包裹段落、`> 入口级说明` 等元说明豁免），
不解析自然语言，不理解语义。

扫描范围：

固定核心扫描文件（GOV001–GOV004，不在此集合中的文件一概不扫描）：

- AGENTS.md
- template/AGENTS.md
- docs/ai/task-levels.md
- docs/ai/branch-strategy.md
- docs/ai/context-index.md
- docs/ai/runbooks/l2-multi-session-runbook.md
- docs/adr/0003-multi-session-l2.md
- docs/adr/0004-l2-spec-and-plan.md
- docs/adr/0005-l3-approval-gate.md

GOV005 额外动态检查（不收口于固定文件集）：

- ``docs/adr/README.md``（按需存在；缺失即 FAIL）
- ``docs/adr/`` 下所有匹配 ``NNNN-<name>.md`` 的 ADR Markdown 文件
  （``README.md`` 与 ``adr-template.md`` 因数字前缀不符而被天然排除）。

规则 ID（固定）：

- GOV001 contradictory-main-policy
- GOV002 contradictory-l2-session-count
- GOV003 merged-spec-plan-fast-path
- GOV004 missing-l3-approval-gate
- GOV005 adr-index-mismatch

退出码：0 = OK（无失败）；1 = Found failures（至少一条 GOV0XX 命中）；
       2 = 参数错误（如 `--root` 指向非目录）。

输出：每条失败一行，格式 ``GOV0XX  file:line  ->  原因片段``（两个空格分隔）。

仅使用 Python 3 标准库；零第三方依赖；只读（不修改任何文件）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# 固定扫描文件集
SCAN_FILES = (
    "AGENTS.md",
    "template/AGENTS.md",
    "docs/ai/task-levels.md",
    "docs/ai/branch-strategy.md",
    "docs/ai/context-index.md",
    "docs/ai/runbooks/l2-multi-session-runbook.md",
    "docs/adr/0003-multi-session-l2.md",
    "docs/adr/0004-l2-spec-and-plan.md",
    "docs/adr/0005-l3-approval-gate.md",
)

# 块级豁免标记：以这些标记开头的 ``>`` 引用块整段跳过
# （涵盖中文 ``已取代`` / ``不重复定义`` 与英文 ``Superseded`` 等效元说明）
BLOCK_EXEMPTION_MARKERS = (
    "> **已取代**",
    "> **不重复定义**",
    "> **Superseded**",
    "> **入口级说明**",
    "> **入口说明**",
    "> Supersedes",  # ADR 状态行的英文 SuperseSSion 标记
)

# 行级豁免关键字：包含这些子串的整行视为元说明，跳过
# （覆盖 ``不再保留过时的`` ``Supersedes`` 等行内声明）
LINE_EXEMPTION_KEYWORDS = (
    "不再保留",
    "不再复述",
    "已过时",
    "Supersedes",
    "Superseded",
)


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------
def iter_check_lines(content: str, template_mode: bool):
    """逐行产出 ``(original_line_no, line_text)``，已豁免的行被跳过。
    行号始终为 1-indexed 的源文件真实行号。
    """
    if not template_mode:
        for i, line in enumerate(content.splitlines(), start=1):
            yield i, line
        return
    in_block = False
    for i, line in enumerate(content.splitlines(), start=1):
        stripped = line.lstrip()
        if any(stripped.startswith(m) for m in BLOCK_EXEMPTION_MARKERS):
            in_block = True
            continue
        if in_block:
            if stripped.startswith(">"):
                continue
            in_block = False
        if any(kw in line for kw in LINE_EXEMPTION_KEYWORDS):
            continue
        yield i, line


def find_matches(content: str, patterns: List[str]) -> List[Tuple[int, str]]:
    """在 content 中找出包含任一 pattern 的所有行；返回 [(行号 1-indexed, 行内容), ...]。"""
    results: List[Tuple[int, str]] = []
    for i, line in iter_check_lines(content, template_mode=False):
        for pat in patterns:
            if pat in line:
                results.append((i, line))
                break
    return results


def rel_path(root: Path, abs_path: Path) -> str:
    """将绝对路径转为相对 root 的 POSIX 字符串。"""
    try:
        return str(abs_path.relative_to(root))
    except ValueError:
        return str(abs_path)


def snippet(line: str, max_len: int = 80) -> str:
    """截取行片段用于输出；去首尾空白后截断。"""
    s = line.strip()
    if len(s) > max_len:
        s = s[: max_len - 1] + "…"
    return s


def read_file_or_empty(root: Path, rel: str) -> str:
    """读取 ``root/rel`` 的内容；不存在则返回空串。"""
    p = root / rel
    if not p.is_file():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


# ---------------------------------------------------------------------------
# 规则实现
# ---------------------------------------------------------------------------
def check_gov001(root: Path, template_mode: bool) -> List[Tuple[str, str, str]]:
    """GOV001 contradictory-main-policy:
    ``docs/ai/task-levels.md`` 同时含 "L0 可在 main" 与 "L0 不得在 main" 语义，
    且后者未在豁免块内 → 报告 FAIL。
    """
    findings: List[Tuple[str, str, str]] = []
    rel = "docs/ai/task-levels.md"
    raw = read_file_or_empty(root, rel)
    if not raw:
        return findings

    positive_patterns = ["L0 可在 main", "L0 允许 main"]
    negative_patterns = [
        "L0 不得在 main",
        "L0 不允许在 main",
        "main 不直接承载开发提交",
        "main / master 不直接承载开发提交",
    ]

    pos = [(i, line) for i, line in iter_check_lines(raw, template_mode) if any(p in line for p in positive_patterns)]
    neg = [(i, line) for i, line in iter_check_lines(raw, template_mode) if any(p in line for p in negative_patterns)]

    if pos and neg:
        line_no, line_text = pos[0]
        neg_line = neg[0][0]
        findings.append(
            (
                "GOV001",
                f"{rel}:{line_no}",
                f"与 line {neg_line} 的 'L0 不得在 main' 冲突: {snippet(line_text)}",
            )
        )
    return findings


def check_gov002(root: Path, template_mode: bool) -> List[Tuple[str, str, str]]:
    """GOV002 contradictory-l2-session-count (跨文件检查):
    AGENTS.md / template/AGENTS.md / docs/adr/0003-multi-session-l2.md 三个权威文件
    中，任意文件同时含 "4 个 session" 与 "3 个 session"（单文件矛盾），或
    三个文件间出现 "4 个 session" 出现在非 `> **已取代**` 豁免块中而其它权威文件已
    收敛为 3 个 session（跨文件不一致）→ 报告 FAIL。
    """
    findings: List[Tuple[str, str, str]] = []
    targets = (
        "AGENTS.md",
        "template/AGENTS.md",
        "docs/adr/0003-multi-session-l2.md",
    )
    old_patterns = ["4 个 session", "4 session 串行"]
    new_patterns = ["3 个 session", "3 session"]

    # 阶段 1：单文件内部矛盾
    for rel in targets:
        raw = read_file_or_empty(root, rel)
        if not raw:
            continue
        old_hits = [(i, line) for i, line in iter_check_lines(raw, template_mode) if any(p in line for p in old_patterns)]
        new_hits = [(i, line) for i, line in iter_check_lines(raw, template_mode) if any(p in line for p in new_patterns)]
        if old_hits and new_hits:
            line_no, line_text = old_hits[0]
            new_line = new_hits[0][0]
            findings.append(
                (
                    "GOV002",
                    f"{rel}:{line_no}",
                    f"单文件矛盾，与 line {new_line} 的 '3 个 session' 冲突: {snippet(line_text)}",
                )
            )

    # 阶段 2：跨文件不一致——权威文件之一仍保留 4 session 现行表述，
    # 但至少有一个权威文件已收敛为 3 session。
    if findings:
        return findings
    cross_old: List[Tuple[str, int, str]] = []
    cross_new: List[Tuple[str, int, str]] = []
    for rel in targets:
        raw = read_file_or_empty(root, rel)
        if not raw:
            continue
        for i, line in iter_check_lines(raw, template_mode):
            if any(p in line for p in old_patterns):
                cross_old.append((rel, i, line))
            if any(p in line for p in new_patterns):
                cross_new.append((rel, i, line))
    if cross_old and cross_new:
        rel, line_no, line_text = cross_old[0]
        findings.append(
            (
                "GOV002",
                f"{rel}:{line_no}",
                f"跨文件矛盾（仍含 4 session），但已有权威文件收敛为 3 session: {snippet(line_text)}",
            )
        )
    return findings


def check_gov003(root: Path, template_mode: bool) -> List[Tuple[str, str, str]]:
    """GOV003 merged-spec-plan-fast-path:
    ``docs/ai/runbooks/l2-multi-session-runbook.md`` 出现 "合并 spec/plan 物理分离"
    且不在 ``> **已取代**`` 块内 → FAIL。
    """
    findings: List[Tuple[str, str, str]] = []
    rel = "docs/ai/runbooks/l2-multi-session-runbook.md"
    raw = read_file_or_empty(root, rel)
    if not raw:
        return findings

    patterns = ["合并 spec/plan 物理分离"]
    hits = [(i, line) for i, line in iter_check_lines(raw, template_mode) if any(p in line for p in patterns)]
    if hits:
        line_no, line_text = hits[0]
        findings.append(
            (
                "GOV003",
                f"{rel}:{line_no}",
                f"合并 spec/plan 物理分离未在 > **已取代** 块: {snippet(line_text)}",
            )
        )
    return findings


def check_gov004(root: Path, template_mode: bool) -> List[Tuple[str, str, str]]:
    """GOV004 missing-l3-approval-gate:
    ``docs/adr/0005-l3-approval-gate.md`` 不存在 → FAIL。
    """
    findings: List[Tuple[str, str, str]] = []
    rel = "docs/adr/0005-l3-approval-gate.md"
    p = root / rel
    if not p.is_file():
        findings.append(
            (
                "GOV004",
                f"{rel}:0",
                "文件缺失（L3 approval gate ADR 必需）",
            )
        )
    return findings


def check_gov005(root: Path, template_mode: bool) -> List[Tuple[str, str, str]]:
    """GOV005 adr-index-mismatch:
    ``docs/adr/README.md`` 索引的同目录 ADR 文件名集合必须与实际文件集合相等。
    """
    del template_mode  # GOV005 没有模板豁免语义
    rel = "docs/adr/README.md"
    readme = root / rel
    if not readme.is_file():
        return [("GOV005", f"{rel}:0", "ADR 索引文件缺失")]

    name_pattern = re.compile(r"[0-9]{4}-[^/\s]+\.md")
    actual = {
        path.name
        for path in readme.parent.iterdir()
        if path.is_file() and name_pattern.fullmatch(path.name)
    }
    raw = read_file_or_empty(root, rel)
    indexed: dict[str, int] = {}
    link_pattern = re.compile(r"\]\(([0-9]{4}-[^/)\s]+\.md)\)")
    for line_no, line in iter_check_lines(raw, template_mode=False):
        for match in link_pattern.finditer(line):
            indexed.setdefault(match.group(1), line_no)

    findings: List[Tuple[str, str, str]] = []
    for name in sorted(actual - indexed.keys()):
        findings.append(("GOV005", f"docs/adr/{name}:0", f"ADR 未在 {rel} 中索引: {name}"))
    for name in sorted(indexed.keys() - actual):
        findings.append(("GOV005", f"{rel}:{indexed[name]}", f"索引目标不存在: {name}"))
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Governance 关键规则一致性检查器（仅标准库）。",
    )
    parser.add_argument("--root", default=".", help="扫描根目录（默认 .）")
    parser.add_argument(
        "--template",
        action="store_true",
        help="启用模板模式（启用 > **已取代** 等元说明豁免）",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root 不是目录: {root}", file=sys.stderr)
        return 2

    all_findings: List[Tuple[str, str, str]] = []
    all_findings.extend(check_gov001(root, args.template))
    all_findings.extend(check_gov002(root, args.template))
    all_findings.extend(check_gov003(root, args.template))
    all_findings.extend(check_gov004(root, args.template))
    all_findings.extend(check_gov005(root, args.template))

    for rule_id, loc, reason in all_findings:
        print(f"{rule_id}  {loc}  ->  {reason}")

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())