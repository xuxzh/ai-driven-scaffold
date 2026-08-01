"""scripts/tests/test_check_markdown_links.py

单元测试：Markdown 链接检查器 (scripts/check-markdown-links.py)。

使用 tempfile.TemporaryDirectory() 构造 fixture，覆盖：
- 有效相对文件链接（跨级 ../）
- 有效相对目录链接
- 外部 URL（http / https）
- 纯锚点（#section）
- 真实断链（missing.md）
- 模板占位符 ([<name>](<app-dir>))
- 代码块内链接应被跳过

只读：所有 fixture 在临时目录创建，测试结束自动清理。
对真实仓库的扫描作为最后一个端到端用例，跑通即视为仓库无断链。
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-markdown-links.py"


def run_checker(root: Path, template: bool = False) -> subprocess.CompletedProcess:
    """执行链接检查器，对 root 进行扫描。"""
    cmd = [sys.executable, str(SCRIPT), "--root", str(root)]
    if template:
        cmd.append("--template")
    return subprocess.run(cmd, capture_output=True, text=True)


class TestCheckMarkdownLinks(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name: str, content: str) -> Path:
        path = self.tmpdir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    # ---- 场景 1：valid.md ----
    def test_valid_md_returns_zero(self):
        # CONTEXT.md 放在 tmpdir 根，valid.md 放在子目录，
        # 这样 [ok](../CONTEXT.md) 从 sub/valid.md 解析正好指向 tmpdir/CONTEXT.md。
        self._write("CONTEXT.md", "# stub\n")
        sub = self.tmpdir / "sub"
        sub.mkdir()
        (sub / "valid.md").write_text(
            "# Valid\n\n"
            "[ok](../CONTEXT.md)\n"
            "[url](https://example.com)\n"
            "[anchor](#section)\n",
            encoding="utf-8",
        )
        result = run_checker(self.tmpdir)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )

    # ---- 场景 2：dir.md ----
    def test_dir_md_returns_zero(self):
        # 链接到同目录子文件夹
        sub = self.tmpdir / "subdir"
        sub.mkdir()
        (sub / "page.md").write_text("# page\n", encoding="utf-8")
        self._write(
            "dir.md",
            "# Dir\n\n"
            "[folder](subdir)\n"
            "[page](subdir/page.md)\n",
        )
        result = run_checker(self.tmpdir)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )

    # ---- 场景 3：template_ok.md ----
    def test_template_ok_md_returns_zero_in_template_mode(self):
        self._write("template_ok.md", "[<name>](<app-dir>)\n")
        result = run_checker(self.tmpdir, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )

    def test_template_placeholder_also_skipped_outside_template(self):
        # 整体被 <...> 包裹的占位符，即使非 template 模式也应被跳过
        self._write("template_ok.md", "[<name>](<app-dir>)\n")
        result = run_checker(self.tmpdir, template=False)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )

    def test_partial_template_placeholder_only_template_mode_skips(self):
        # 路径中含 <name> 或以 ... 结尾，non-template 模式会报为断链；template 模式会跳过
        # 用新的临时目录隔离第二次调用
        with tempfile.TemporaryDirectory() as tmp2:
            tmp2 = Path(tmp2)
            (tmp2 / "doc.md").write_text(
                "[tpl1](../ai/<name>.md)\n[tpl2](../some/path.md...)\n",
                encoding="utf-8",
            )
            tpl = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent.parent / "check-markdown-links.py"),
                    "--root",
                    str(tmp2),
                    "--template",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(tpl.returncode, 0, msg=tpl.stderr)
            non_tpl = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent.parent / "check-markdown-links.py"),
                    "--root",
                    str(tmp2),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(non_tpl.returncode, 1, msg=non_tpl.stderr)

    def test_url_encoded_link_resolves_to_existing_file(self):
        # 创建带空格的文件名，链接用 %20 编码
        self._write("Hello World.md", "# Hi\n")
        self._write("doc.md", "[hi](Hello%20World.md)\n")
        result = run_checker(self.tmpdir)
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    # ---- 场景 4：broken.md ----
    def test_broken_md_returns_one(self):
        self._write("broken.md", "[bad](missing.md)\n")
        result = run_checker(self.tmpdir)
        self.assertEqual(
            result.returncode,
            1,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        combined = result.stdout + result.stderr
        self.assertIn("broken.md:1", combined)

    # ---- 补充：协议链接 / 锚点 / 带 fragment 与 title 的链接 ----
    def test_protocol_and_anchor_links_skipped(self):
        # extras.md 放在子目录，CONTEXT.md 在 tmpdir 根，
        # 这样 ../CONTEXT.md 从 sub/extras.md 能解析到 tmpdir/CONTEXT.md
        self._write("CONTEXT.md", "# stub\n")
        sub = self.tmpdir / "sub"
        sub.mkdir()
        (sub / "extras.md").write_text(
            "# Extras\n\n"
            "[http](http://example.com)\n"
            "[mailto](mailto:a@b.com)\n"
            "[ftp](ftp://example.com/x)\n"
            "[anchor-only](#section-2)\n"
            "[with-fragment](../CONTEXT.md#anchor)\n"
            "[with-title](../CONTEXT.md \"title here\")\n",
            encoding="utf-8",
        )
        result = run_checker(self.tmpdir)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )

    # ---- 补充：代码块内链接应被跳过 ----
    def test_link_inside_fenced_code_block_skipped(self):
        self._write(
            "codeblock.md",
            "# CodeBlock\n\n"
            "```markdown\n"
            "[bad](missing.md)\n"
            "```\n",
        )
        result = run_checker(self.tmpdir)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


class TestEndToEndRepo(unittest.TestCase):
    """对真实仓库（只读）跑一次链接检查；不应有断链。"""

    def test_repo_scan_with_template(self):
        result = run_checker(REPO_ROOT, template=True)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )


if __name__ == "__main__":
    unittest.main()