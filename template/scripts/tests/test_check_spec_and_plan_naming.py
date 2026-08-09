"""scripts/tests/test_check_spec_and_plan_naming.py

单元测试：spec / plan 命名检查器 (scripts/check-spec-and-plan-naming.py)。

使用 tempfile.TemporaryDirectory() 构造 fixture，覆盖：
- 合法命名（典型 kebab-case name）
- 合法命名（闰年 2028-02-29）
- 合法命名（同日并行后缀 -2）
- 非法命名（日期格式错 2026-8-1）
- 非法命名（月份越界 2026-13）
- 非法命名（非闰年的 02-29）
- 非法命名（name 含下划线 / 大写 / 空 / 连续连字符 / 收尾连字符）
- 缺目录（两目录均缺失 → 退出 0）
- 缺目录（单目录缺失 → 不影响另一目录的判定）
- 非法根（--root 指向不存在路径 → 退出 2）
- 跨目录排序（plans 行先于 specs 行）
- 同日后缀 -1 / 全数字 name 被 NAME_RE 接受
- 真实仓库端到端扫描（只读）

只读：所有 fixture 在临时目录创建，测试结束自动清理。
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-spec-and-plan-naming.py"


def run_checker(root: Path) -> subprocess.CompletedProcess:
    """执行命名检查器，对 root 进行扫描。"""
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

    # 合法:task-packets 目录的合法命名应通过(TARGET_DIRS 须含 docs/task-packets)
    def test_valid_task_packets_return_zero(self):
        self._write("docs/task-packets", "2026-08-01-pkt.md")
        self.assertEqual(run_checker(self.tmpdir).returncode, 0)

    # 非法:task-packets 目录的非法命名应报违例
    def test_invalid_task_packets_return_one(self):
        self._write("docs/task-packets", "foo.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/task-packets/foo.md", result.stdout)

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
        self._write("docs/plans", "aaa.md")
        self._write("docs/specs", "bbb.md")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 1, msg=result.stdout)
        lines = result.stdout.splitlines()
        # 全局字典序下 docs/plans/aaa.md 必须先于 docs/specs/bbb.md
        self.assertLess(
            lines.index("docs/plans/aaa.md"),
            lines.index("docs/specs/bbb.md"),
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