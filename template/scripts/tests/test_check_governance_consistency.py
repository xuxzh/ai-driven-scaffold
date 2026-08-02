"""scripts/tests/test_check_governance_consistency.py

单元测试：治理一致性检查器 (scripts/check-governance-consistency.py)。

覆盖规则：
- GOV001 contradictory-main-policy
- GOV002 contradictory-l2-session-count
- GOV003 merged-spec-plan-fast-path
- GOV004 missing-l3-approval-gate
- GOV005 adr-index-mismatch

每个失败 fixture 都用 tempfile.TemporaryDirectory() 构造 mini repo，
只写入触发该规则的最小文件集，避免其他规则误触发。

最后两类：
- pass fixture：所有规则都用 `> **已取代**` 块包装或完整文件存在，期望 PASS。
- end-to-end：对真实仓库 (`--root . --template`) 跑一次，期望 exit 0。

只读：所有 fixture 在临时目录创建，测试结束自动清理。
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-governance-consistency.py"


def run_checker(root: Path, template: bool = False) -> subprocess.CompletedProcess:
    """执行一致性检查器，对 root 进行扫描。"""
    cmd = [sys.executable, str(SCRIPT), "--root", str(root)]
    if template:
        cmd.append("--template")
    return subprocess.run(cmd, capture_output=True, text=True)


class _FixtureBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)
        self.write("docs/adr/README.md", "")

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, content: str) -> Path:
        path = self.tmpdir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if rel.startswith("docs/adr/") and re.fullmatch(r"[0-9]{4}-[^/]+\.md", path.name):
            readme = self.tmpdir / "docs/adr/README.md"
            if readme.is_file():
                names = sorted(p.name for p in readme.parent.glob("[0-9][0-9][0-9][0-9]-*.md"))
                readme.write_text("".join(f"[{name}]({name})\n" for name in names), encoding="utf-8")
        return path


# ----------------------------------------------------------------------
# GOV001 contradictory-main-policy
# ----------------------------------------------------------------------
class TestGOV001ContradictoryMainPolicy(_FixtureBase):
    """task-levels.md 同时含 "L0 可在 main" 与 "L0 不得在 main"。
    Non-template 模式应 FAIL；模板模式 + > **已取代** 块豁免应 PASS。"""

    def test_non_template_with_both_phrases_fails(self):
        self.write(
            "docs/ai/task-levels.md",
            "# Task Levels\n\n"
            "## L0\n\n"
            "L0 可在 main 直接落盘。\n\n"
            "## 主分支保护\n\n"
            "L0 不得在 main / master 上直接落盘。\n",
        )
        result = run_checker(self.tmpdir, template=False)
        self.assertEqual(
            result.returncode,
            1,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        combined = result.stdout + result.stderr
        self.assertIn("GOV001", combined)

    def test_template_mode_with_superseded_block_passes(self):
        self.write(
            "docs/ai/task-levels.md",
            "# Task Levels\n\n"
            "## L0 旧规（已取代）\n\n"
            "> **已取代**：\n"
            "> L0 可在 main 直接落盘。\n\n"
            "## 主分支保护\n\n"
            "L0 不得在 main / master 上直接落盘。\n",
        )
        # 让 GOV004 不误触：补齐 ADR-0005
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        # Template 模式：> **已取代** 块豁免掉 "L0 可在 main" → 应 PASS
        tpl = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            tpl.returncode,
            0,
            msg=f"stdout={tpl.stdout!r}\nstderr={tpl.stderr!r}",
        )
        # Non-template 模式：无豁免，应 FAIL
        non_tpl = run_checker(self.tmpdir, template=False)
        self.assertEqual(
            non_tpl.returncode,
            1,
            msg=f"stdout={non_tpl.stdout!r}\nstderr={non_tpl.stderr!r}",
        )

    def test_no_contradiction_passes(self):
        # 只有 "L0 不得在 main"，无 "L0 可在 main"
        self.write(
            "docs/ai/task-levels.md",
            "# Task Levels\n\n"
            "## 主分支保护\n\n"
            "L0 不得在 main / master 上直接落盘。\n",
        )
        # 让 GOV004 不误触：补齐 ADR-0005
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        result = run_checker(self.tmpdir, template=False)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


# ----------------------------------------------------------------------
# GOV002 contradictory-l2-session-count
# ----------------------------------------------------------------------
class TestGOV002ContradictoryL2SessionCount(_FixtureBase):
    """AGENTS.md 与 ADR-0003 同时含 '4 个 session' 与 '3 个 session'，
    ADR-0003 未含 > **已取代** 块 → FAIL。"""

    def test_both_files_with_both_phrases_no_superseded_fails(self):
        self.write(
            "AGENTS.md",
            "# AGENTS\n\n"
            "## session\n\n"
            "L2 必须 4 个 session 串行。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        self.write(
            "docs/adr/0003-multi-session-l2.md",
            "# ADR-0003\n\n"
            "## session\n\n"
            "L2 必须 4 个 session 串行。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            1,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        combined = result.stdout + result.stderr
        self.assertIn("GOV002", combined)

    def test_only_three_session_passes(self):
        # 只有 "3 个 session"，无 "4 个 session"
        self.write(
            "AGENTS.md",
            "# AGENTS\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        self.write(
            "docs/adr/0003-multi-session-l2.md",
            "# ADR-0003\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        # 让 GOV004 不误触：补齐 ADR-0005
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )

    def test_line_number_preserved_with_superseded_block(self):
        # 在 > **已取代** 块前后插入 4 session 表述，验证行号不被重编号
        self.write(
            "AGENTS.md",
            "line 1\n"
            "line 2\n"
            "line 3\n"
            "> **已取代**：本节仅供历史参考。\n"
            "L2 任务按 4 个 session 串行（已过时）。\n"
            "> 后续以 3 个 session 为准。\n"
            "line 7\n",
        )
        self.write(
            "docs/adr/0003-multi-session-l2.md",
            "# ADR-0003\n\nL2 走 3 个 session。\n",
        )
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        # non-template 模式下应报 GOV002 且行号严格保留 5 (原 4 session 表述所在行)
        result2 = run_checker(self.tmpdir, template=False)
        self.assertEqual(result2.returncode, 1)
        self.assertIn("AGENTS.md:5", result2.stdout + result2.stderr)

    def test_pure_cross_file_inconsistency_fails(self):
        # 纯跨文件不一致：AGENTS.md 仍含 4 session 现行表述（豁免块外），
        # 但 ADR-0003 已收敛为 3 session。
        self.write(
            "AGENTS.md",
            "# AGENTS\n\n"
            "L2 走 3 个 session 串行。\n"
            "## 历史\n"
            "L2 任务按 4 个 session 串行（旧表述，未标记已取代）。\n",
        )
        self.write(
            "docs/adr/0003-multi-session-l2.md",
            "# ADR-0003\n\nL2 走 3 个 session 串行。\n",
        )
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        combined = result.stdout + result.stderr
        self.assertIn("GOV002", combined)
        self.assertIn("AGENTS.md:5", combined)


# ----------------------------------------------------------------------
# GOV003 merged-spec-plan-fast-path
# ----------------------------------------------------------------------
class TestGOV003MergedSpecPlanFastPath(_FixtureBase):
    """runbook 中出现 "合并 spec/plan 物理分离" 且未在 > **已取代** 块 → FAIL。"""

    def test_phrase_outside_superseded_block_fails(self):
        self.write(
            "docs/ai/runbooks/l2-multi-session-runbook.md",
            "# Runbook\n\n"
            "## 快速通道\n\n"
            "允许 L2 任务规模 < 半天时合并 spec/plan 物理分离。\n",
        )
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            1,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        combined = result.stdout + result.stderr
        self.assertIn("GOV003", combined)

    def test_phrase_in_superseded_block_passes(self):
        self.write(
            "docs/ai/runbooks/l2-multi-session-runbook.md",
            "# Runbook\n\n"
            "## 完成定义\n\n"
            "> **已取代**：\n"
            "> 允许 L2 任务规模 < 半天时合并 spec/plan 物理分离。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        # 让 GOV004 不误触：补齐 ADR-0005
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


# ----------------------------------------------------------------------
# GOV004 missing-l3-approval-gate
# ----------------------------------------------------------------------
class TestGOV004MissingL3ApprovalGate(_FixtureBase):
    """docs/adr/ 缺少 0005-l3-approval-gate.md → FAIL。"""

    def test_missing_approval_gate_file_fails(self):
        # adr 目录存在但 0005 文件缺失
        self.write(
            "docs/adr/0003-multi-session-l2.md",
            "# ADR-0003 stub\n",
        )
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            1,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        combined = result.stdout + result.stderr
        self.assertIn("GOV004", combined)

    def test_approval_gate_file_present_passes(self):
        self.write(
            "docs/adr/0005-l3-approval-gate.md",
            "# ADR-0005 stub\n",
        )
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


# ----------------------------------------------------------------------
# GOV005 adr-index-mismatch
# ----------------------------------------------------------------------
class TestGOV005AdrIndexMismatch(_FixtureBase):
    """README 索引必须与 docs/adr/ 下实际 ADR 文件名集合完全一致。"""

    def test_missing_readme_fails(self):
        (self.tmpdir / "docs/adr/README.md").unlink()
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("GOV005  docs/adr/README.md:0", result.stdout)

    def test_actual_adr_absent_from_index_fails(self):
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        self.write("docs/adr/README.md", "# ADR index\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("GOV005", result.stdout)
        self.assertIn("0005-l3-approval-gate.md", result.stdout)

    def test_indexed_target_without_actual_adr_fails(self):
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        self.write(
            "docs/adr/README.md",
            "[ADR-0005](0005-l3-approval-gate.md)\n"
            "[ADR-0006](0006-nonexistent.md)\n",
        )
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("GOV005", result.stdout)
        self.assertIn("0006-nonexistent.md", result.stdout)

    def test_matching_sets_have_no_gov005_finding(self):
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        self.write(
            "docs/adr/README.md",
            "[ADR-0005](0005-l3-approval-gate.md)\n",
        )
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertNotIn("GOV005", result.stdout + result.stderr)


# ----------------------------------------------------------------------
# Pass fixture：所有规则都用 > **已取代** 包装或文件存在
# ----------------------------------------------------------------------
class TestPassFixture(_FixtureBase):
    """完整 mini repo fixture，所有规则都通过豁免 / 完整文件保证 PASS。"""

    def _build_pass_fixture(self):
        # task-levels.md："L0 可在 main" 在 > **已取代** 块中
        self.write(
            "docs/ai/task-levels.md",
            "# Task Levels\n\n"
            "## L0 旧规\n\n"
            "> **已取代**：\n"
            "> L0 可在 main 直接落盘。\n\n"
            "## 主分支保护\n\n"
            "L0 不得在 main / master 上直接落盘。\n",
        )
        # AGENTS.md："4 个 session" 在 > **不重复定义** 块中
        self.write(
            "AGENTS.md",
            "# AGENTS\n\n"
            "> **不重复定义**：不再复述 4 个 session 串行等过时表述。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        self.write(
            "template/AGENTS.md",
            "# AGENTS\n\n"
            "> **不重复定义**：不再复述 4 个 session 串行等过时表述。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        # ADR-0003："4 个 session" 在 > **已取代** 块中
        self.write(
            "docs/adr/0003-multi-session-l2.md",
            "# ADR-0003\n\n"
            "> **已取代**：\n"
            "> L2+ 必须 4 个 session 串行的旧规已被取代。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        # ADR-0004、ADR-0005 完整存在
        self.write("docs/adr/0004-l2-spec-and-plan.md", "# ADR-0004 stub\n")
        self.write("docs/adr/0005-l3-approval-gate.md", "# ADR-0005 stub\n")
        # runbook："合并 spec/plan 物理分离" 在 > **已取代** 块中
        self.write(
            "docs/ai/runbooks/l2-multi-session-runbook.md",
            "# Runbook\n\n"
            "> **已取代**：\n"
            "> 允许 L2 任务规模 < 半天时合并 spec/plan 物理分离。\n\n"
            "L2 走 3 个 session 串行。\n",
        )
        # branch-strategy 与 context-index（扫描列表中的其他文件）
        self.write("docs/ai/branch-strategy.md", "# Branch\n")
        self.write("docs/ai/context-index.md", "# Context\n")

    def test_pass_fixture_in_template_mode(self):
        self._build_pass_fixture()
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


# ----------------------------------------------------------------------
# 端到端：对真实仓库扫描
# ----------------------------------------------------------------------
class TestEndToEndRepo(unittest.TestCase):
    """对真实仓库（只读）跑一次一致性检查；不应有失败。"""

    def test_repo_scan_with_template(self):
        result = run_checker(REPO_ROOT, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


if __name__ == "__main__":
    unittest.main()