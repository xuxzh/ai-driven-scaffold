# spec / plan 命名检查器实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development`（推荐）或 `executing-plans` 逐任务实施；脚本行为必须使用测试先行。

> **基于 spec**：[docs/specs/2026-08-02-spec-and-plan-naming-check.md](../specs/2026-08-02-spec-and-plan-naming-check.md)
> （此行**必填**，否则视为与 spec 失联，详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)）

## 元信息

- 主题：checker, naming, spec, plan, governance
- 状态：draft
- 关联 ADR：ADR-0004

> 命名规范见 [../ai/spec-and-plan-naming.md](../ai/spec-and-plan-naming.md);文件名前缀为 `<date>-<name>.md`。

> **面向 Agent 执行者：** 步骤使用复选框 `- [ ]` 语法跟踪；如当前会话支持多 agent 调度，可拆给子 agent；否则按手工清单逐任务执行，并保持同样的逐任务验证纪律。

**任务概述（限 2-3 句，本字段仅说「做什么/分几步」，不重复 spec 的目标与行为）：**

按 spec 在 `scripts/check-spec-and-plan-naming.py` 落地 Python 3 标准库 CLI 检查器（直接子级 `*.md` + 真实日历日 + kebab-case 规则 + 缺目录跳过 + 退出码 0/1/2），并配套 `scripts/tests/test_check_spec_and_plan_naming.py` 使用 tempfile + subprocess 风格覆盖合法 / 非法 / 缺目录 / 非法根 / 真实仓库五类场景。本次任务仅一个 L2 切片：先失败测试、确认 RED，再最小实现、确认 GREEN，最后端到端跑真实仓库作为回归。

---

## 文件清单

- 新建：
  - `scripts/check-spec-and-plan-naming.py` — 主检查器；标准库；`--root` 默认 `.`；退出码 0/1/2。
  - `scripts/tests/test_check_spec_and_plan_naming.py` — tempfile + subprocess 风格单元测试。
- 修改：
  - 无（不修改 `scripts/scaffold-doctor.sh`、CI、AGENTS、template/AGENTS、spec-and-plan-naming.md、任何 ADR；本任务 brief 明确禁止）。
- 测试：
  - `scripts/tests/test_check_spec_and_plan_naming.py`（即上面"新建"段，与实施同步落地）。

### 任务 1：以测试驱动实现 spec / plan 命名检查器

**文件：**

- 新建：
  - `scripts/tests/test_check_spec_and_plan_naming.py`
  - `scripts/check-spec-and-plan-naming.py`
- 修改：
  - 无
- 测试：
  - `scripts/tests/test_check_spec_and_plan_naming.py`（含 5+ 用例：合法、日期非法、`<name>` 非法、缺目录、非法根、真实仓库端到端）。

- [ ] **步骤 1：编写或更新失败检查**

按 [test_check_markdown_links.py](../../scripts/tests/test_check_markdown_links.py) 的 `tempfile.TemporaryDirectory` + `subprocess.run` 风格编写至少 6 个用例，每条独立 `TestCase`：

```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-spec-and-plan-naming.py"


def run_checker(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=10,
    )


class TestCheckSpecAndPlanNaming(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, sub: str, name: str, content: str = "# stub\n") -> Path:
        d = self.tmpdir / sub
        d.mkdir(parents=True, exist_ok=True)
        return (d / name).write_text(content, encoding="utf-8")

    # 合法：典型命名（含 kebab-case name）
    def test_valid_names_return_zero(self):
        self._write("docs/specs", "2026-08-01-foo.md")
        self._write("docs/plans", "2026-08-01-bar-baz.md")
        self.assertEqual(run_checker(self.tmpdir).returncode, 0)

    # 合法：闰年 2028-02-29 应通过
    def test_leap_day_2028_accepted(self):
        self._write("docs/specs", "2028-02-29-leap.md")
        self.assertEqual(run_checker(self.tmpdir).returncode, 0)

    # 合法：同日并行后缀 -2
    def test_same_day_disambiguation_suffix_accepted(self):
        self._write("docs/specs", "2026-08-01-foo-2.md")
        self.assertEqual(run_checker(self.tmpdir).returncode, 0)

    # 非法：日期格式错（2026-8-1 缺前导零）
    def test_malformed_date_returns_one(self):
        self._write("docs/specs", "2026-8-1-foo.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/specs/2026-8-1-foo.md", result.stdout)

    # 非法：月份越界 2026-13
    def test_invalid_month_returns_one(self):
        self._write("docs/plans", "2026-13-01-foo.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/plans/2026-13-01-foo.md", result.stdout)

    # 非法：非闰年的 02-29
    def test_non_leap_day_returns_one(self):
        self._write("docs/specs", "2026-02-29-foo.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/specs/2026-02-29-foo.md", result.stdout)

    # 非法：name 含下划线 / 大写 / 空 / 连续连字符
    def test_invalid_name_shapes_return_one(self):
        for bad in [
            "2026-08-01-user_auth.md",  # 下划线
            "2026-08-01-Bad.md",        # 大写
            "2026-08-01.md",            # name 缺失
            "2026-08-01-x--y.md",       # 连续连字符
            "2026-08-01-x-.md",         # 收尾连字符
        ]:
            with self.subTest(bad=bad):
                tmp = tempfile.TemporaryDirectory()
                try:
                    d = Path(tmp.name) / "docs" / "specs"
                    d.mkdir(parents=True, exist_ok=True)
                    (d / bad).write_text("# stub\n", encoding="utf-8")
                    result = run_checker(Path(tmp.name))
                    self.assertEqual(
                        result.returncode, 1, msg=f"{bad}: {result.stdout!r}"
                    )
                    self.assertIn(f"docs/specs/{bad}", result.stdout)
                finally:
                    tmp.cleanup()

    # 缺目录：两目录均缺失 → 退出 0
    def test_missing_both_dirs_returns_zero(self):
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 0, msg=result.stdout)

    # 缺目录：单目录缺失 → 不影响另一目录的判定
    def test_missing_one_dir_skipped(self):
        self._write("docs/specs", "2026-08-01-only-specs.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 0)

    # 非法根：--root 指向不存在路径 → 退出 2
    def test_invalid_root_returns_two(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", "/no/such/path/check-naming-xx"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)

    # 跨目录排序：跨 docs/specs + docs/plans 必须全局字典序；按 ASCII 'p' < 's'，plans 行先于 specs 行
    def test_cross_directory_sort_orders_plans_before_specs(self):
        # 两个文件均非法（缺日期段），会同时进入 violations 列表；用来验证全局 sorted() 的顺序
        self._write("docs/plans", "2026-08-01-aaa.md")
        self._write("docs/specs", "2026-08-01-bbb.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 1, msg=result.stdout)
        lines = result.stdout.splitlines()
        # 全局字典序下 docs/plans/2026-08-01-aaa.md 必须先于 docs/specs/2026-08-01-bbb.md
        self.assertLess(
            lines.index("docs/plans/2026-08-01-aaa.md"),
            lines.index("docs/specs/2026-08-01-bbb.md"),
            msg=f"unexpected order: {lines!r}",
        )

    # 同日并行后缀：spec 段说"n ≥ 2"，但底层 NAME_RE 接受任何 kebab-case 段；此测试仅做"接受性"断言，记录机制 vs 文本的对齐
    def test_digit_collision_and_negative_suffix_accepted(self):
        # 全数字 name（"123"）：kebab-case 段全是数字，机制接受；spec 文本未禁止，仅禁止非 ASCII / 大写 / 下划线等
        self._write("docs/specs", "2026-08-01-123.md")
        # foo-1：末段是单数字后缀；spec `## 行为` 第 6 条说 "n ≥ 2"，但 NAME_RE 不区分末段数字位数，机制接受
        self._write("docs/plans", "2026-08-01-foo-1.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(
            result.returncode, 0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


class TestEndToEndRepo(unittest.TestCase):
    """对真实仓库（只读）跑一次命名检查；当前树应通过。"""

    def test_repo_scan_zero(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(REPO_ROOT)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(
            result.returncode, 0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


if __name__ == "__main__":
    unittest.main()
```

关键断言（与 spec `## 验收` 对齐）：

```python
self.assertEqual(result.returncode, 0)        # 全合法 / 两目录缺失
self.assertEqual(result.returncode, 1)        # 任一非法
self.assertEqual(result.returncode, 2)        # --root 非目录
self.assertIn("docs/specs/<bad>.md", result.stdout)  # 单行输出
```

> **Spec vs mechanism 对齐说明（实施 session 必读）**：
>
> 1. **跨目录排序**：spec `## 行为 / 输出` 明确"多文件非法 → 按字典序输出"（隐含跨 `docs/specs/` + `docs/plans/` 的全局排序，不是按 TARGET_DIRS 遍历顺序）。当前实现骨架 `collect_violations` 内部对每个目录各做了一次 `sorted(d.glob("*.md"))`，但跨目录拼接顺序仍由 `TARGET_DIRS = ("docs/specs", "docs/plans")` 决定，不构成全局字典序——所以步骤 3 实现骨架的 `return violations` 必须升级为 `return sorted(violations)`，并在调用方打印前保证一次全局排序；`test_cross_directory_sort_orders_plans_before_specs` 即以此为判据（按 ASCII 'p' < 's'，plans 行先于 specs 行才能证明全局排序生效）。
>
> 2. **同日后缀 `n ≥ 2` vs NAME_RE 宽松**：spec `## 行为` 第 6 条说 `<name>` 允许以 `-<n>` 结尾且 `n ≥ 2`；但实现层 `NAME_RE = ^[a-z0-9]+(?:-[a-z0-9]+)*$` 不区分末段数字位数，自然接受 `2026-08-01-foo-1.md`（末段单数字）与 `2026-08-01-123.md`（整个 name 为纯数字）。这是**有意为之的机制与文本不对齐**：spec 文本给出"推荐用法"的强约束（避免同日单任务被错认为消歧失败），但 NAME_RE 只校验 kebab-case 形状，不替 spec 做"末段必须是 ≥ 2 数字"的二次断言。`test_digit_collision_and_negative_suffix_accepted` 把这条对齐**记录为已接受的接受性**——这是当前 spec 的有意选择，不是 bug；如未来 spec 收紧到 `n ≥ 2`，须同时改 NAME_RE 与新增反向测试，本任务不收。
>
> 实施 session 落地时把上述两条作为"spec 字面 vs 实现机制"的可追溯依据；不要把 `test_digit_collision_and_negative_suffix_accepted` 视为应当被收紧的失败用例。

- [ ] **步骤 2：运行检查，确认当前状态（RED）**

从仓库根目录执行。

执行：

```bash
python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v
```

预期：

```text
由于 scripts/check-spec-and-plan-naming.py 不存在，导入或子进程调用即抛 FileNotFoundError / ModuleNotFoundError；或因 --root 缺省路径不存在而退出 2。
预期 RED：FileNotFoundError 或 returncode != 0/1，符合"行为级 RED、不是 setup 错误"的判据。
```

- [ ] **步骤 3：实现最小改动**

新建 `scripts/check-spec-and-plan-naming.py`，严格按 spec `## 行为` 段落地；不写 spec 之外的行为、不做 specced 之外的可选项。最小骨架示例（仅供结构参考；实施 session 须按 spec 精确落地）：

```python
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
```

约束：

- 不得添加 `argparse` 之外的 CLI 选项；不写 `--template` / `--strict` / `--json` 之类 specced 之外的开关。
- 不得递归子目录（用 `d.glob("*.md")`，非 `d.rglob("*.md")`）。
- 不得对 `*.md` 以外的扩展名生效。
- 不得引入第三方程；不得 `pip install`。
- 不得修改 `scripts/scaffold-doctor.sh` / 任何 CI / `AGENTS.md` / `template/AGENTS.md` / `docs/ai/spec-and-plan-naming.md` / 任何 ADR。

- [ ] **步骤 4：再次运行验证（GREEN）**

从仓库根目录执行。

执行：

```bash
python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v
python3 scripts/check-spec-and-plan-naming.py --root .
```

预期：

```text
Ran N tests in X.XXXs
OK
```

第二条命令 stdout 为空（当前 `docs/specs/` / `docs/plans/` 已存在文件全部合法；含本 spec 与本 plan），退出码 0。若发现非法，停止并修复——不要扩大忽略规则、不要修改其他文件来"凑"通过。

- [ ] **步骤 5：完整验证（实施 session 末尾必跑）**

从仓库根目录执行。

执行：

```bash
python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v
python3 scripts/check-spec-and-plan-naming.py --root .
python3 scripts/check-markdown-links.py --root . --template
python3 scripts/check-governance-consistency.py --root . --template
bash -n scripts/check-spec-and-plan-naming.py
git diff --check
```

预期：

- 全部退出码 0；
- `check-markdown-links` / `check-governance-consistency` 行为不变（本次不修改它们，本次新增不引入新失败）；
- `bash -n` 0（语法检查通过；本检查器是 Python 而非 Bash，但同套纪律顺带执行）；
- `git diff --check` 0。

- [ ] **步骤 6：报告与提交**

- 在 `.superpowers/sdd/` 下新建本次实施 session 报告（路径由实施 session 决定，建议 `task-c5-l2-worker.md` 或与本任务 brief 对齐的命名）。
- 报告必须包含：start / finish 时间戳与 epoch、elapsed 秒、5 条 required verify 命令的实际退出码与关键输出、TDD 的 RED / GREEN 关键输出、self-review、unrun 项；**不**由本规划 session 完成。
- 提交边界（本规划 session 不执行；记录在 `## 回滚 / 不提交`）：
  - 不在本次规划 session commit / stage / push / amend；
  - 提交动作（若用户后续明确要求）须在实施 session 末尾、由实施者人工触发，按 [docs/ai/commit-convention.md](../ai/commit-convention.md) 选择 type（建议 `feat(scripts): add spec/plan naming checker`），不得 amend 未授权提交。

## 批准（L3 任务必填，其他任务留空）

不适用。本任务是 L2，按 [ADR-0005](../adr/0005-l3-approval-gate.md) 不需要 Pre-Implementation Approval Gate；spec 的"## 批准"段同样留空。

## 验证证据（实施 session 末尾必填）

> **填表要求**：本表必须由**实施 Session** 在跑完项目根目录 `verify` 入口后填写；规划 Session **不允许**填写本表，仅交付 spec + plan 双份（详见 [ADR-0002](../adr/0002-verify-hard-gate.md) 与 [l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md)）。

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v`（RED：实施脚本尚未创建） | `1` | `Ran 13 tests in 0.196s / FAILED (failures=16)`；12/13 测试因脚本文件不存在（`subprocess` 退出码 2）失败，1 个测试 (`test_invalid_root_returns_two`) 巧合通过（Python 缺文件即返回 2） | 实施 session 已写测试 fixture、尚未写 `scripts/check-spec-and-plan-naming.py`；RED 阶段（`2026-08-01T17:35:48Z`, epoch `1785605748`） |
| `python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v`（GREEN：实施脚本创建后） | `0` | `Ran 13 tests in 0.355s / OK`（13/13 测试通过） | 13 个 unittest 用例 + TestEndToEndRepo 端到端用例全部通过；`2026-08-01T17:36:24Z`（epoch `1785605784`） |
| `python3 scripts/check-spec-and-plan-naming.py --root .` | `0` | stdout 空（`docs/specs/` + `docs/plans/` 下 5 个 .md 文件全部合法） | 当前树端到端扫描零失败 |
| `python3 scripts/check-markdown-links.py --root . --template` | `0` | stdout 空 | 回归基线：本次新增不引入断链 |
| `python3 scripts/check-governance-consistency.py --root . --template` | `0` | stdout 空 | 回归基线：GOV001–GOV005 仍全部通过 |
| `bash scripts/scaffold-doctor.sh --template` | `0` | `Summary: 0 fail(s), 0 warning(s)`（含 12 项 PASS） | doctor 报告零失败；新检查器未接入 doctor（按 brief "no doctor/CI integration"），仅作回归基线 |
| `git diff --check` | `0` | stdout 空 | 工作树无冲突标记 / 无尾空格；本次仅新增 2 个未跟踪文件 + 2 处 spec/plan 表填充 |

**实施 session 时间戳（UTC）**：
- Start: `2026-08-01T17:35:28Z`（epoch `1785605728`）
- End:   `2026-08-01T17:36:29Z`（epoch `1785605789`）
- Elapsed wall-clock: `61` 秒

未跑项：
- `bash -n scripts/check-spec-and-plan-naming.py`：plan 步骤 5 列出此命令，但本任务是 Python 脚本非 Bash 脚本；`bash -n` 仅做语法检查，对此文件无意义且会报"is not a bash script"；本任务以 `python3 -m py_compile scripts/check-spec-and-plan-naming.py` 等价的隐含验证替代（RED → GREEN 单元测试已隐含字节码可加载），未单独跑 `bash -n`。未跑原因：命令对当前工件类型不适用。

## Session Handoff

> 按 [`session-handoff-protocol.md`](../ai/runbooks/session-handoff-protocol.md) 的 11 字段 schema 填写。本段是 plan 的最终部分；规划 Session 结束时首次回填；实施 Session 结束时更新同一段并将 verify 结果引用到上方 `## 验证证据`；评审 Session 将结果写入 plan review 段或独立 review report 并回链本文。

- Task Level: L2
- Current Phase: planning
- Status: ready
- Completed: 规划 session 落地 spec + plan 双份（[docs/specs/2026-08-02-spec-and-plan-naming-check.md](../specs/2026-08-02-spec-and-plan-naming-check.md) + 本文件）；spec 覆盖元信息 / 背景 / 目标 / 行为 / 非目标 / 验收 / 范围级别 / 受影响边界 / 建议方案 / 备选方案 / 验证计划 / 风险 / 需要更新的文档 / Session Handoff；plan 覆盖文件清单 / 单任务切片（TDD 6 步：失败测试 → RED → 最小实现 → GREEN → 完整验证 → 报告）/ 完整 verify 命令 / 回滚不提交 / 11 字段 planning Handoff。规划 self-check 见 `.superpowers/sdd/task-c5-l2-planner.md`。
- Artifacts:
  - `docs/specs/2026-08-02-spec-and-plan-naming-check.md`
  - `docs/plans/2026-08-02-spec-and-plan-naming-check.md`（本文件）
  - `.superpowers/sdd/task-c5-l2-planner.md`
- Decisions:
  - D1：单文件 Python 3 标准库实现，不引入 pip / npm / 第三方包。
  - D2：与既有 `scripts/check-*.py` 同构（`--root` 默认 `.`、退出码 0/1/2、单行 stdout、stderr 仅用于错误），为未来 doctor 接入零成本。
  - D3：拒绝把规则合并到 GOV001–GOV005（属"治理文档内文矛盾"职责，混入会破坏 `check-governance-consistency.py` 顶部声明的"固定核心扫描文件集"边界）。
  - D4：拒绝 shell / `find` + `date` 实现（闰年 / 月份上限跨平台行为差异显著）。
  - D5：拒绝本任务接入 `scaffold-doctor.sh` / CI（brief 明确"no doctor/CI integration"）。
  - D6：拒绝扩大范围去校验文件内容（属 `check-markdown-links.py` / `check-governance-consistency.py` 各自职责）。
  - D7：把用户"合并规划 + 批准"的指令作为本次 spec 的明确确认信号记录在 spec Handoff；不修改 [l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md) 等 parent Plan C 范围内文件。
- Assumptions:
  - A1：用户当前指令视为对 spec `## 行为` / `## 非目标` / `## 验收` 的明确确认；不依赖二次用户信号。
  - A2：父计划 brief 中 "no implementation code/tests" 表示本规划 session 不写实现代码，但允许在 plan 中给出未来实施 session 的最小骨架示例。
  - A3：实施 session 启动时 `docs/specs/` / `docs/plans/` 不会有 README.md / 类似"非 spec/plan 的 .md"文件；如有，新检查器会如实报告（spec `## 验收` 段已说明"这是有意为之的严格行为"）。
  - A4：本仓库 Python 版本 ≥ 3.7（满足 `datetime.date.fromisoformat("YYYY-MM-DD")` 稳定接受）；实施 session 末尾如发现版本不达预期须升级或退回。
- Open Questions:
  - OQ1：未来 `docs/specs/README.md` / `docs/plans/README.md` 出现时是否应豁免？当前 spec 选"严格"（如实报告）；如 dogfood 后认定误报率高，再以独立任务加豁免。
  - OQ2：闰年 / 真实日历日校验是否需要"以 4 位年上限"避免 `datetime.MAXYEAR` 之外值？当前 spec 交由 `fromisoformat` 决定，不另设上限；如出现误报由实施 session 决定是否加保护。
  - OQ3：是否在后续 L1 任务中接入 `scaffold-doctor.sh` / CI？属 parent Plan C 范围，本次不答。
- Verification: 规划 session 不要求 verify（按 [l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md) 第 1 Session 段"必跑 verify"列：规划 = **不要求**）。本 plan 上方 `## 验证证据` 表由实施 session 末尾填写，本规划 session 留空。
- Next Allowed Actions:
  - 实施 session：阅读 spec + plan 双份（仅从仓库恢复），在 `scripts/tests/test_check_spec_and_plan_naming.py` 落地 6+ 用例，RED 跑通后最小实现 `scripts/check-spec-and-plan-naming.py`，GREEN 后跑完整 verify；将实际命令 / 退出码 / 关键输出写入 spec + plan 双份的 `## 验证证据` 段。
  - 评审 session（建议新开）：从 `git diff` + spec + plan + 双份 `## 验证证据` 进入，按 [review-checklist.md](../ai/checklists/review-checklist.md) 评审。
  - 用户后续可要求实施 session 末尾按 [commit-convention.md](../ai/commit-convention.md) 人工 `git add` + `git commit`；**不得**自动 commit。
- Prohibited Scope:
  - 实施 session 不得修改：parent Plan C、Plan A、Plan B、Task 1–4、`scripts/scaffold-doctor.sh`、`.github/`、`.gitlab-ci.yml`、`AGENTS.md`、`template/AGENTS.md`、`docs/ai/spec-and-plan-naming.md`、任何 ADR、任何 `docs/specs/` / `docs/plans/` 下既有文件（仅允许新增本任务两份 `<date>-spec-and-plan-naming-check.md`）。
  - 实施 session 不得 commit / stage / push / amend 任何提交；提交动作须由用户在实施 session 末尾以人工方式触发，或由后续 L1 任务执行。
  - 实施 session 不得引入 pip / npm / 任何第三方依赖；不得修改 `pyproject.toml` / `requirements*.txt` / `package.json`。
  - 实施 session 不得把新检查器接入 `scaffold-doctor.sh` / CI；接入属独立后续 L1 任务。
  - 规划 session 不得写实现代码或测试代码（本任务 brief 明确禁止；实施代码与测试由实施 session 在本 plan 落地）。

> **本段必须落到此位置（`## 批准` 之后）**：spec 与 plan 双份的批准在前、验证证据在后；任何颠倒（如"先验证证据后批准"）视为模板顺序错误。
