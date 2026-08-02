#!/usr/bin/env python3
"""check-spec-and-plan-naming.py — docs/specs / docs/plans 命名只读检查器

仅校验 ``<root>/docs/specs/*.md`` 与 ``<root>/docs/plans/*.md`` 的直接子级
文件名是否匹配 ``<YYYY-MM-DD>-<kebab-name>.md``：

- 日期段须为 ``YYYY-MM-DD`` 且是真实日历日（``datetime.date.fromisoformat`` 可解析）
- ``<name>`` 段非空、仅小写 ASCII 字母 / 数字 / 单连字符
- 任一目录缺失：跳过该目录（不计入失败）
- 退出码：0 = 全部合法 / 无对象；1 = 至少一个非法；2 = ``--root`` 非目录

仅使用 Python 3 标准库；零第三方依赖；只读（不修改任何文件）。
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

TARGET_DIRS = ("docs/specs", "docs/plans")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-(.+))?$")


def validate_stem(stem: str) -> bool:
    """True iff ``stem`` 形如 ``YYYY-MM-DD`` + 非空 kebab-name。"""
    m = DATE_PREFIX_RE.match(stem)
    if not m:
        return False
    date_str, name = m.group(1), m.group(2)
    try:
        date.fromisoformat(date_str)
    except ValueError:
        return False
    if not name:  # 缺 name
        return False
    return bool(NAME_RE.match(name))


def collect_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for sub in TARGET_DIRS:
        d = root / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if not f.is_file():
                continue
            try:
                rel = f.relative_to(root).as_posix()
            except ValueError:
                rel = str(f)
            if not validate_stem(f.stem):
                violations.append(rel)
    # spec `## 行为 / 输出` 要求"按字典序输出"：跨两个 target 目录做一次全局排序
    return sorted(violations)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="docs/specs 与 docs/plans 命名只读检查器（仅标准库）。"
    )
    parser.add_argument("--root", default=".", help="扫描根目录（默认 .）")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root 不是目录: {root}", file=sys.stderr)
        return 2

    violations = collect_violations(root)
    for v in violations:
        print(v)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())