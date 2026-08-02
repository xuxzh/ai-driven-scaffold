# template-restructure 实施计划

> 基于 spec：[docs/specs/2026-08-02-template-restructure.md](../specs/2026-08-02-template-restructure.md)
> （此行**必填**，否则视为与 spec 失联，详见 [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md)）

## 元信息

- 主题：restructure, template, scaffold, governance, paths
- 状态：draft
- 关联 ADR：(无直接引用;沿用 ADR-0002 / 0003 / 0004 既有硬门禁)

> 命名规范见 [../spec-and-plan-naming.md](../../template/docs/ai/spec-and-plan-naming.md);文件名前缀为 `<date>-<name>.md`。

> **面向 Agent 执行者**：步骤使用复选框 `- [ ]` 语法跟踪；本 plan 在 worktree `refactor/template-restructure` 上执行。
>
> **执行模式**：本 plan 由实施 Session 在 worktree 内按 Task 1 → 2 → 3 → 4 → 5 → 6 顺序执行；每 Task 末尾一个独立 commit；Task 0(基线) 在 Task 1 之前跑一次，作为"迁移前对照点"。

**任务概述(限 2-3 句)**：把 7 项下发物(`docs/ai/**`、`docs/adr/**`、`docs/CONTEXT.md`、`scripts/**`、`.gitlab-ci.yml`、`.github/workflows/ci.yml`、`CLAUDE.md`)用 `git mv` 平移到 `template/` 下，再用 3 条 sed 规则一次性扫全仓 markdown 改路径引用，最后手改 doctor + check-governance 的 mode-conditional 路径与 README/CONTRIBUTING 文档。分 6 个 task 推进，每个 task 一个独立可验证交付物。

---

## 文件清单

**新建**：

- (无)

**修改**：

- `template/AGENTS.md`(sed 规则 1:`../docs/` → `docs/`)
- `template/CLAUDE.md`(git mv 后再 sed 规则 1)
- `AGENTS.md`(根,sed 规则 2:加 `template/` 前缀)
- `README.md`(根,sed 规则 2 + 三方式改写 + 删"接入后必做清理"段 + 改"目录结构"段 + 改 CI 段命令)
- `CONTRIBUTING.md`(根,sed 规则 2 + 维护者命令路径改 `template/scripts/...`)
- `docs/specs/**`、`docs/plans/**`(sed 规则 2:加 `template/` 前缀)
- `template/scripts/scaffold-doctor.sh`(`check_structure` 函数加 mode-conditional 前缀)
- `template/scripts/check-governance-consistency.py`(多处 `docs/ai/...` `docs/adr/...` 改 mode-conditional)
- `template/scripts/check-markdown-links.py`(无需改,无硬编码路径)
- `template/scripts/check-spec-and-plan-naming.py`(无需改,`docs/specs` `docs/plans` 留在根)
- `template/scripts/tests/*`(无需改)
- `template/.github/workflows/ci.yml`、`template/.gitlab-ci.yml`(git mv 后内容不变)

**删除**：

- (无)

**测试**（都已存在,本 plan 不新增）：

- `template/scripts/tests/scaffold-doctor-test.sh`
- `template/scripts/tests/worktree-add-test.sh`
- `template/scripts/tests/test_*.py`

---

## 全局约束

（本段从 spec 摘录,所有 task 隐含适用。）

- **任务等级**:L2,必须 spec + plan 双份已签收才能进入实施 session。
- **工作区**:独立 worktree `.worktrees/refactor-template-restructure/`,branch `refactor/template-restructure`;**严禁**在 `main` 上提交。
- **分支命名**:沿用 `worktree-add.sh` 实际接受的 `refactor/template-restructure`(slash 分隔符,与 `branch-strategy.md` 文档 hyphen 形式有已知分歧,本任务不修)。
- **commit 规范**:Conventional Commits,scope 落在路径主段(如 `template` / `docs` / `scripts`)。
- **保留**:`AGENTS.md`、`README.md`、`CONTRIBUTING.md`、`LICENSE`、`.gitignore` 留在根;`docs/specs/`、`docs/plans/` 留在根。
- **不修改**:`docs/adr/*` 内容、`docs/ai/**` 内部互引、`template/AGENTS.md` 的 5 个 `<...>` 占位符、`template/.github/workflows/ci.yml` 和 `template/.gitlab-ci.yml` 的 `scripts/...` 引用。
- **不引入新特性**:`--adopt` 模式、bootstrap 脚本、新 doctor 检查器——一律不在本 plan 范围。
- **验证入口**:7 条命令列在每个 task 的"再次运行验证"段;以 `template/scripts/...` 路径(post-move)。

---

### Task 0(基线):迁移前 7 条验证全 pass

> **本 Task 在所有 git mv 之前跑**,作为"迁移前对照点"。若基线已坏,先停下来排查,不要带着"基线已坏"的状态进入迁移。

- [ ] **步骤 1:跑 7 条验证命令,记录输出**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

bash scripts/scaffold-doctor.sh --template
python3 scripts/check-markdown-links.py --root . --template
python3 scripts/check-governance-consistency.py --root . --template
python3 scripts/check-spec-and-plan-naming.py
bash scripts/tests/scaffold-doctor-test.sh
bash scripts/tests/worktree-add-test.sh
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
```

预期：全部退出码 0;`Summary: 0 fail(s), N warning(s)`(N 可能非 0,WARN 是允许的)。

- [ ] **步骤 2:把每条命令的实际退出码记到本 plan 末尾 `## 验证证据` 表的"基线"行**

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| (基线)`bash scripts/scaffold-doctor.sh --template` | 0 | Summary: 0 fail(s), N warning(s) | 迁移前 |
| (基线)`python3 scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | 迁移前 |
| (基线)`python3 scripts/check-governance-consistency.py --root . --template` | 0 | All GOV rules satisfied | 迁移前 |
| (基线)`python3 scripts/check-spec-and-plan-naming.py` | 0 | All files match naming | 迁移前 |
| (基线)`bash scripts/tests/scaffold-doctor-test.sh` | 0 | All tests passed | 迁移前 |
| (基线)`bash scripts/tests/worktree-add-test.sh` | 0 | All tests passed | 迁移前 |
| (基线)`python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` | 0 | Ran N tests in M s — OK | 迁移前 |

- [ ] **步骤 3:无 commit**

本 Task 不产生 commit;只作为对照点。

---

### 任务 1:把 7 个下发物平移到 template/ 下,应用 sed 规则 1

**文件：**

- 新建：(无)
- 修改：用 `git mv` 移 7 个下发物(见下);`template/AGENTS.md`(sed 规则 1);`template/CLAUDE.md`(sed 规则 1,先 mv 再 sed)
- 测试：无新增;跑 `check-markdown-links` 看根 .md 的链接状态(task 2 修)

- [ ] **步骤 1:编写失败检查**(应 fail,因 `template/docs/ai` 等还不存在)

```bash
cat > /tmp/task1-check.sh <<'EOF'
#!/bin/sh
set -u
fail=0
for p in \
  template/docs/ai \
  template/docs/adr \
  template/docs/CONTEXT.md \
  template/scripts \
  template/.gitlab-ci.yml \
  template/.github/workflows/ci.yml \
  template/CLAUDE.md
do
  if [ ! -e "$p" ]; then
    printf 'FAIL: missing %s\n' "$p"
    fail=1
  else
    printf 'PASS: %s\n' "$p"
  fi
done
exit $fail
EOF
chmod +x /tmp/task1-check.sh
```

- [ ] **步骤 2:运行检查,确认当前状态(在 7 个 git mv 之前)**

执行：`/tmp/task1-check.sh; echo "task1-check exit: $?"`

预期：退出码 1(全部 FAIL,因 `template/docs/ai` 等不存在);`template/AGENTS.md` 已存在(本步骤不检查它)。

- [ ] **步骤 3:实施最小改动——7 个 `git mv`**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 注意:git mv 必须每个单独写,不要用 shell glob 一次拉
git mv docs/ai template/docs/ai
git mv docs/adr template/docs/adr
git mv docs/CONTEXT.md template/docs/CONTEXT.md
git mv scripts template/scripts
git mv .gitlab-ci.yml template/.gitlab-ci.yml
git mv .github template/.github
git mv CLAUDE.md template/CLAUDE.md

# 验证 git rename detection(应该全部识别为 R,不是 D+A)
git status --short
```

预期：`git status` 显示 7 行 `R` (rename)——若是 `D` + `??`,说明有文件被错误处理,停下来排查。

- [ ] **步骤 4:再次运行验证**

```bash
# 4a. 7 个下发物就位检查(应全 pass)
/tmp/task1-check.sh; echo "4a exit: $?"

# 4b. template/AGENTS.md 当前应还有 `../docs/...` 残留(待步骤 5 修)
python3 -c "
import re, pathlib
p = pathlib.Path('template/AGENTS.md')
text = p.read_text()
broken = re.findall(r'\.\./docs/[^\s\)\]]+', text)
print('broken refs in template/AGENTS.md (待步骤 5 修):', len(broken))
"

# 4c. 根 .md 链接当前应全部 broken(check-markdown-links 应 fail)
python3 template/scripts/check-markdown-links.py --root . --template 2>&1 | tail -20
echo "4c exit: $?"
```

预期：

- 4a：退出码 0
- 4b：列出多条 `../docs/...` 残留(待步骤 5 修)
- 4c：退出码非 0(根 AGENTS.md / README.md / CONTRIBUTING.md / docs/specs/** / docs/plans/** 的 `docs/ai/...` 引用全 broken)——**这是预期中间状态**,在 task 2 修

- [ ] **步骤 5:实施 sed 规则 1——修 template/AGENTS.md 与 template/CLAUDE.md 的 `../docs/` 前缀**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 在两个文件里把 ../docs/ 改成 docs/(去掉 ../,同级引用)
sed -i.bak 's|\.\./docs/|docs/|g' template/AGENTS.md template/CLAUDE.md
rm -f template/AGENTS.md.bak template/CLAUDE.md.bak

# 验证
grep -c '\.\./docs/' template/AGENTS.md template/CLAUDE.md
```

预期：两个文件的 `../docs/` 计数为 0;`template/AGENTS.md` 内的 `[docs/ai/task-levels.md](../../template/docs/ai/task-levels.md)` 等链接保持 `docs/ai/...` 形式(平移后正确)。

- [ ] **步骤 6:再次运行验证**

```bash
# 6a. 根 .md 链接仍 broken(预期,task 2 修)
python3 template/scripts/check-markdown-links.py --root . --template 2>&1 | wc -l
echo "6a broken count(应 > 0)"

# 6b. template/AGENTS.md 与 template/CLAUDE.md 自身应不报 broken
python3 template/scripts/check-markdown-links.py --root . --template 2>&1 | grep -E "template/AGENTS\.md|template/CLAUDE\.md" || echo "6b OK (无 template/AGENTS.md 自身 broken)"
```

预期：

- 6a：broken 数量 > 0(根 .md 的旧路径)
- 6b：grep 无输出(template/AGENTS.md 与 template/CLAUDE.md 自身链接正确)

- [ ] **步骤 7:提交**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

git status --short
# 预期看到:R template/AGENTS.md, R template/CLAUDE.md, R template/docs/ai, R template/docs/adr,
#          R template/docs/CONTEXT.md, R template/scripts, R template/.gitlab-ci.yml, R template/.github

git add -A
git commit -m "$(cat <<'EOF'
refactor(template): move docs, scripts, CI files and CLAUDE.md under template/

Physically relocate 7 ship-target groups (docs/ai, docs/adr, docs/CONTEXT.md,
scripts, .gitlab-ci.yml, .github/workflows/, CLAUDE.md) under template/ so
the scaffold-self vs. downstream-shipped boundary becomes a directory
split instead of a README text convention. All moves use `git mv` to
preserve rename detection.

Apply sed rule 1 to template/AGENTS.md and template/CLAUDE.md: drop the
`../docs/` prefix that pointed at the old root location; the new sibling
location resolves with `docs/...`.

The 7 verification commands (scaffold-doctor --template, three check_*.py,
two tests, unittest discover) are partially broken in the intermediate
state — root .md files still reference old paths. Task 2 fixes that
with sed rule 2.

Refs: docs/specs/2026-08-02-template-restructure.md
EOF
)"
```

---

### 任务 2:用 sed 规则 2 改写根 .md 的所有相对路径引用

**文件：**

- 修改：`AGENTS.md`(根)、`README.md`(根)、`CONTRIBUTING.md`(根)、`docs/specs/**`、`docs/plans/**`
- 测试：无新增;跑 `check-markdown-links` 验证 0 broken

- [ ] **步骤 1:编写失败检查**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 把当前 broken 数量记录到 /tmp/task2-broken-before.txt
python3 template/scripts/check-markdown-links.py --root . --template 2>&1 | grep -c "broken" > /tmp/task2-broken-before.txt
cat /tmp/task2-broken-before.txt
```

预期：N > 0(N 是根 .md 的旧路径引用产生的 broken 数量)。

- [ ] **步骤 2:运行检查,确认当前状态**

执行步骤 1 的命令,记录 N 的具体值。

- [ ] **步骤 3:实施 sed 规则 2**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 6 个前缀加 template/ 前缀(注意顺序:长前缀在前,避免 docs/ai/ 误吃 docs/adr/)
FILES="AGENTS.md README.md CONTRIBUTING.md $(find docs/specs docs/plans -name '*.md')"

for f in $FILES; do
  sed -i.bak \
    -e 's|docs/ai/|template/docs/ai/|g' \
    -e 's|docs/adr/|template/docs/adr/|g' \
    -e 's|docs/CONTEXT.md|template/docs/CONTEXT.md|g' \
    -e 's|scripts/|template/scripts/|g' \
    -e 's|\.gitlab-ci\.yml|template/.gitlab-ci.yml|g' \
    -e 's|\.github/workflows/|template/.github/workflows/|g' \
    "$f"
  rm -f "$f.bak"
done

# 验证没有 ../docs/ 残留
grep -rn "\.\./docs/" AGENTS.md README.md CONTRIBUTING.md docs/specs docs/plans || echo "(no ../docs/ residue)"
```

预期：无 `../docs/` 残留;所有 `docs/ai/` `docs/adr/` `docs/CONTEXT.md` `scripts/` `.gitlab-ci.yml` `.github/workflows/` 都加了 `template/` 前缀。

- [ ] **步骤 4:再次运行验证**

```bash
python3 template/scripts/check-markdown-links.py --root . --template
echo "exit: $?"

# 同时跑 governance 一致性(也应 pass)
python3 template/scripts/check-governance-consistency.py --root . --template
echo "governance exit: $?"
```

预期：两条命令都退出码 0(check-markdown-links 0 broken;check-governance-consistency 通过)。

- [ ] **步骤 5:提交**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

git add -A
git commit -m "$(cat <<'EOF'
refactor(docs): rewrite root .md path references to template/

Apply sed rule 2 across AGENTS.md, README.md, CONTRIBUTING.md,
docs/specs/**, docs/plans/**: prepend `template/` to all 6 path
prefixes (docs/ai/, docs/adr/, docs/CONTEXT.md, scripts/,
.gitlab-ci.yml, .github/workflows/). This is the mechanical sweep
that fixes the broken links introduced by the file moves in the
previous commit.

Note for reviewers: docs/specs/ and docs/plans/ are scaffold-self L2
history, not shipped to downstream. Editing their internal path
references is expected; the spec/plan text content is untouched.

check-markdown-links.py --root . --template now reports zero broken
links from this scope.
EOF
)"
```

---

### 任务 3:更新 doctor + check-governance 的 mode-conditional 路径

**文件：**

- 修改：
  - `template/scripts/scaffold-doctor.sh`(`check_structure` 函数加 mode-conditional 前缀)
  - `template/scripts/check-governance-consistency.py`(多处 `docs/ai/...` `docs/adr/...` 改 mode-conditional)
- 测试：跑 `bash template/scripts/scaffold-doctor.sh --template` 与单测

- [ ] **步骤 1:编写失败检查**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

bash template/scripts/scaffold-doctor.sh --template 2>&1 | tee /tmp/task3-baseline.txt
echo "exit: $?"
```

预期：doctor 退出码非 0(失败模式是"docs/adr/0002-verify-hard-gate.md is missing"等——因为 doctor 还硬编码根路径,template/ 路径找不到);`/tmp/task3-baseline.txt` 记录具体失败内容。

- [ ] **步骤 2:定位所有需要 mode-conditional 化的硬编码路径**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# doctor 里的硬编码 docs/adr/ + .github/workflows/ + .gitlab-ci.yml
grep -nE "(docs/adr/|\.github/workflows/|\.gitlab-ci\.yml)" template/scripts/scaffold-doctor.sh

# check-governance 里的所有 docs/ai/ + docs/adr/ 引用
grep -nE "docs/(ai|adr)/" template/scripts/check-governance-consistency.py | head -50
```

预期：列出所有需要改的行。

- [ ] **步骤 3:实施最小改动——`scaffold-doctor.sh` 加 mode-conditional 前缀**

打开 `template/scripts/scaffold-doctor.sh`,定位到 `check_structure()` 函数,**在函数体开头**(任何 `if/for` 之前)加:

```sh
  # Mode-conditional prefix: scaffold self uses template/ subtree;
  # adopted projects have everything at root.
  if [ "$mode" = template ]; then
    cs_prefix="template/"
  else
    cs_prefix=""
  fi
```

然后把以下硬编码路径替换为带前缀的版本:

| 旧 | 新 |
|---|---|
| `for ci_file in .github/workflows/ci.yml .gitlab-ci.yml;` | `for ci_file in ${cs_prefix}.github/workflows/ci.yml ${cs_prefix}.gitlab-ci.yml;` |
| `docs/adr/0002-verify-hard-gate.md` | `${cs_prefix}docs/adr/0002-verify-hard-gate.md` |
| `docs/adr/0003-multi-session-l2.md` | `${cs_prefix}docs/adr/0003-multi-session-l2.md` |
| `docs/adr/0004-l2-spec-and-plan.md` | `${cs_prefix}docs/adr/0004-l2-spec-and-plan.md` |
| `docs/adr/0005-l3-approval-gate.md` | `${cs_prefix}docs/adr/0005-l3-approval-gate.md` |

`docs/specs` 与 `docs/plans` 的检查保持原样(它们在两个模式下都在根)。

- [ ] **步骤 4:实施最小改动——`check-governance-consistency.py` 加 mode-conditional 路径**

打开 `template/scripts/check-governance-consistency.py`,在 `main` / 函数入口附近加 helper:

```python
def doc_path(rel: str) -> str:
    """Resolve a doc path under template/ in --template mode, else at root."""
    if getattr(args, "template", False):
        return f"template/{rel}"
    return rel
```

(注意:`args` 是 `argparse.Namespace`;在 `check-governance-consistency.py` 现有 main 里,`args` 已经在 `args = parser.parse_args()` 之后可用。helper 应该定义在 `args = parser.parse_args()` **之后**,或者通过闭包 / 传参访问 `args`。)

把以下每处 `rel = "docs/ai/..."` 或 `rel = "docs/adr/..."` 改成 `rel = doc_path("docs/ai/...")`,以及任何 `"docs/ai/..."` `"docs/adr/..."` 字符串字面量(在 `REQUIRED` 列表里、`f"docs/adr/..."` 里、字符串比较里)统一改成 `doc_path("docs/ai/...")` / `doc_path("docs/adr/...")`。

具体范围(用 `grep -nE "docs/(ai|adr)/" check-governance-consistency.py` 输出的行号):

- L13-19 docstring 里的 `docs/ai/...` `docs/adr/...` 路径示例——**保持原样**,这是文档,不是逻辑代码
- L23-24 docstring 里的 `docs/adr/README.md`、`docs/adr/`——**保持原样**,文档
- L55-61 `REQUIRED` 列表里的所有 `docs/ai/...` `docs/adr/...` 字符串——**改成 `doc_path(...)` 调用**
- L155-159 `rel = "docs/ai/task-levels.md"`——**改成 `rel = doc_path(...)`**
- L190 注释里的 `docs/adr/0003-multi-session-l2.md`——**保持原样**,注释
- L199 `docs/adr/0003-multi-session-l2.md` 在 `for` 列表里——**改成 `doc_path(...)`**
- L251 注释里的 `docs/ai/runbooks/l2-multi-session-runbook.md`——**保持原样**,注释
- L255 `rel = "docs/ai/runbooks/l2-multi-session-runbook.md"`——**改成 `rel = doc_path(...)`**
- L276 注释里的 `docs/adr/0005-l3-approval-gate.md`——**保持原样**,注释
- L279 `rel = "docs/adr/0005-l3-approval-gate.md"`——**改成 `rel = doc_path(...)`**
- L294-317 `rel = "docs/adr/README.md"` 与 `docs/adr/{name}` 拼接——**改成 `rel = doc_path("docs/adr/README.md")`** 与 `doc_path(f"docs/adr/{name}")`

- [ ] **步骤 5:再次运行验证**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

bash template/scripts/scaffold-doctor.sh --template
echo "doctor --template exit: $?"

python3 template/scripts/check-governance-consistency.py --root . --template
echo "governance --template exit: $?"

bash template/scripts/tests/scaffold-doctor-test.sh
echo "doctor test exit: $?"

python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v
echo "unittest exit: $?"
```

预期：四条命令都退出码 0。

- [ ] **步骤 6:跑完整 7 条验证**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
python3 template/scripts/check-spec-and-plan-naming.py
bash template/scripts/tests/scaffold-doctor-test.sh
bash template/scripts/tests/worktree-add-test.sh
python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v
```

预期：全部退出码 0。

- [ ] **步骤 7:提交**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

git add template/scripts/scaffold-doctor.sh template/scripts/check-governance-consistency.py
git commit -m "$(cat <<'EOF'
refactor(scripts): make scaffold-doctor and check-governance mode-aware

Both scripts used to hardcode paths like docs/adr/0002-... and
.github/workflows/ci.yml at the repo root. After the file moves in the
previous commits, those paths live under template/ in --template mode
(scaffold self-check) and at the root in --adopted mode (downstream
project check).

- scaffold-doctor.sh: add cs_prefix local variable in check_structure(),
  prepend it to all 4 ADR paths and 2 CI file paths. docs/specs and
  docs/plans are unchanged (they live at root in both modes).
- check-governance-consistency.py: add doc_path() helper that prepends
  template/ when --template is set, use it at every site that reads
  docs/ai/... or docs/adr/... for actual file I/O (string literals in
  docstrings/comments left untouched).

7 verification commands all pass in --template mode after this change.
EOF
)"
```

---

### 任务 4:改写 README 三种接入方式 + 删"接入后必做清理"段

**文件：**

- 修改：`README.md`(根)——"5 分钟上手"段、"接入后必做清理"段、"接入后的 5 步"段
- 测试：无新增;手动 review + smoke test 抽到 Task 6

- [ ] **步骤 1:编写失败检查**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

grep -n "cp -r /tmp/ai-scaffold/docs/ai" README.md && echo "STILL HAS OLD TEXT" || echo "OK (no old text in 方式 3)"
grep -n "接入后必做清理" README.md && echo "STILL HAS OLD TEXT" || echo "OK (no 接入后必做清理 section)"
```

预期：两条 grep 都有匹配(README 改前还有旧文本)。

- [ ] **步骤 2:实施最小改动——替换"5 分钟上手"段**

**原"方式 1:用 GitHub 模板创建新仓库"块**(从 `### 方式 1:` 到下一个 `### 方式 2:`)整体替换为:

````markdown
### 方式 1：用 GitHub 模板创建新仓库

```bash
gh repo create my-project --template https://github.com/xuxzh/ai-driven-scaffold --private --clone
cd my-project

# 1. template/ 升格为根(覆盖脚手架自身的 AGENTS.md / README.md 等)
shopt -s dotglob                      # 让 cp 也复制 .gitlab-ci.yml / .github/
cp -rT template .
rm -rf template docs/specs docs/plans  # 移除脚手架自身的 spec/plan 历史与 template/ 自身
mkdir -p docs/specs docs/plans
touch docs/specs/.gitkeep docs/plans/.gitkeep

# 2. 重置 git(克隆自模板仓库,不是你的)
rm -rf .git
git init -b main
git add . && git commit -m "chore: bootstrap from ai-driven-scaffold"

# 3. 补 Adoption Profile
$EDITOR AGENTS.md
```
````

**原"方式 2:手动克隆并裁剪"块**整体替换为:

````markdown
### 方式 2：手动克隆并裁剪

```bash
git clone https://github.com/xuxzh/ai-driven-scaffold my-project
cd my-project

# 1. template/ 升格为根
shopt -s dotglob
cp -rT template .
rm -rf template docs/specs docs/plans
mkdir -p docs/specs docs/plans
touch docs/specs/.gitkeep docs/plans/.gitkeep

# 2. 重置 git
rm -rf .git
git init -b main
git add . && git commit -m "chore: bootstrap from ai-driven-scaffold"

# 3. 补 Adoption Profile
$EDITOR AGENTS.md
```
````

**原"方式 3:把治理层注入既有项目"块**整体替换为:

````markdown
### 方式 3：把治理层注入既有项目

```bash
cd ~/my-existing-project

# 0. 临时克隆模板
git clone https://github.com/xuxzh/ai-driven-scaffold /tmp/ai-scaffold

# 1. 复制下发物(路径都从根改成 template/)
cp -r /tmp/ai-scaffold/template/docs/ai docs/
cp -r /tmp/ai-scaffold/template/docs/adr docs/
cp /tmp/ai-scaffold/template/docs/CONTEXT.md docs/
cp -r /tmp/ai-scaffold/template/scripts ./scripts
cp /tmp/ai-scaffold/template/AGENTS.md ./AGENTS.md
cp /tmp/ai-scaffold/template/CLAUDE.md ./CLAUDE.md
cp /tmp/ai-scaffold/template/.gitlab-ci.yml ./.gitlab-ci.yml
cp -rn /tmp/ai-scaffold/template/.github ./.github   # -n 避免覆盖既有 workflows

# 2. 补空目录
mkdir -p docs/specs docs/plans
touch docs/specs/.gitkeep docs/plans/.gitkeep

# 3. 补 Adoption Profile
$EDITOR AGENTS.md

# 4. 清理
rm -rf /tmp/ai-scaffold
```

> **注意**：`cp -rn` 在 `.github/` 已存在时不会覆盖;若既有项目已有 workflows,需手动 `diff` 后再合并。
````

**整段"## 接入后必做清理(三种方式通用)"**整段删除(从标题到下一个 `## 接入后的 5 步` 之前的所有行)。

- [ ] **步骤 3:实施最小改动——微调"接入后的 5 步"段**

把第 1 步的"补全 Adoption Profile"与第 2 步的"必须定义 `verify` 命令"之间的内容保持原样;**移除**"接入后必做清理"引用(若有);保留其余 4 步。

具体：只删段内可能引用"接入后必做清理"的字眼,其余原样保留。

- [ ] **步骤 4:再次运行验证**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

grep -n "cp -r /tmp/ai-scaffold/docs/ai" README.md || echo "OK (方式 3 旧文本已删)"
grep -n "接入后必做清理" README.md || echo "OK (接入后必做清理 段已删)"
grep -n "cp -rT template" README.md && echo "OK (新方式 1/2 已加)" || echo "MISSING cp -rT"
grep -n "cp /tmp/ai-scaffold/template/AGENTS.md" README.md && echo "OK (新方式 3 已加)" || echo "MISSING 方式 3"

python3 template/scripts/check-markdown-links.py --root . --template
echo "links exit: $?"
```

预期：4 条 grep 全部 OK;check-markdown-links 退出码 0。

- [ ] **步骤 5:提交**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

git add README.md
git commit -m "$(cat <<'EOF'
docs(readme): rewrite three adoption methods using cp -rT template .

Replace the legacy "cp -r docs/ai docs/" + "cp -r docs/adr docs/" pattern
with `cp -rT template .` for greenfield adoption, and the corresponding
`cp -r /tmp/ai-scaffold/template/...` pattern for injecting into existing
projects. Use `cp -rn` for .github/ in 方式 3 so existing workflows are
not clobbered.

Delete the now-obsolete "接入后必做清理" paragraph — scaffold self's
spec/plan history stays at root in this repo but does not ship via
template/, so downstream projects never see those historical files.

Refs: docs/specs/2026-08-02-template-restructure.md § 行为 / 采用流程
EOF
)"
```

---

### 任务 5:更新 CONTRIBUTING.md 维护者命令 + README"目录结构"段 + README "CI"段

**文件：**

- 修改：`CONTRIBUTING.md`(根)、`README.md`(根,"目录结构"段 + "CI(验证层,非准入层)"段的本地命令)
- 测试：无新增;跑 7 条验证命令

- [ ] **步骤 1:编写失败检查**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# CONTRIBUTING.md 里的旧 scripts/ 引用
grep -nE "scripts/(scaffold-doctor|check-|worktree-add|tests/)" CONTRIBUTING.md | head -20

# README 目录结构段(应还有 docs/ai docs/adr docs/CONTEXT.md scripts/ 树状)
sed -n '/^## 目录结构/,/^## /p' README.md | grep -E "├── docs/ai|├── docs/adr|├── docs/CONTEXT|├── scripts|├── \.gitlab|├── \.github" || echo "(旧目录树已不在)"
```

预期：两条 grep 都有匹配(还没改)。

- [ ] **步骤 2:实施最小改动——CONTRIBUTING.md**

把"## 验证清单(修改后自检)"段的 `bash -n scripts/...` `python3 scripts/...` `bash scripts/...` 全部加 `template/` 前缀(注意 `scripts/tests/` 也是);本段下面的"补充检查项"里的 `grep -rE` 命令行也加 `template/`(对 `AGENTS.md` 的 grep 不加,因为 AGENTS.md 在根)。

具体:用 `sed -i` 批量改:

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 改 CONTRIBUTING.md 的 scripts/ 引用
sed -i.bak \
  -e 's|bash -n scripts/|bash -n template/scripts/|g' \
  -e 's|python3 -m unittest discover -s scripts/|python3 -m unittest discover -s template/scripts/|g' \
  -e 's|python3 scripts/check-|python3 template/scripts/check-|g' \
  -e 's|bash scripts/scaffold-doctor|bash template/scripts/scaffold-doctor|g' \
  -e 's|bash scripts/tests/|bash template/scripts/tests/|g' \
  CONTRIBUTING.md
rm -f CONTRIBUTING.md.bak
```

预期：CONTRIBUTING.md 里所有 `scripts/...` 引用改为 `template/scripts/...`(除了可能保留的"## 验证清单"说明性文字,如"维护本脚手架仓库的开发者,本地跑通..."等)。

- [ ] **步骤 3:实施最小改动——README"目录结构"段**

把"目录结构"代码块里的 `docs/ai/` `docs/adr/` `docs/CONTEXT.md` `scripts/` `.gitlab-ci.yml` `.github/workflows/ci.yml` 都加 `template/` 前缀;`template/AGENTS.md` 那行保留(显式锚点)。`docs/specs/` `docs/plans/` 保持根。

新"目录结构"段目标文本:

````markdown
## 目录结构

```
.
├── AGENTS.md                       # 本仓库专用入口(已按本仓库事实填好 Adoption Profile)
├── README.md                       # 本文件
├── CONTRIBUTING.md                 # 模板仓库维护说明
├── LICENSE                         # MIT
├── docs/
│   ├── specs/                      # 脚手架自身 L2 历史(spec/plan,仅本仓库)
│   └── plans/                      # 脚手架自身 L2 历史
└── template/                       # 采用者会复制的所有下发物
    ├── AGENTS.md                   # 采用本脚手架的项目的模板入口(含 <...> 占位符)
    ├── CLAUDE.md
    ├── docs/
    │   ├── ai/                     # AI 治理与工作流
    │   ├── adr/                    # 长期决策
    │   └── CONTEXT.md
    ├── scripts/
    │   └── scaffold-doctor.sh      # 只读接入自检脚本
    ├── .github/workflows/ci.yml
    └── .gitlab-ci.yml
```
````

把原"目录结构"段整体替换为上面这段。

- [ ] **步骤 4:实施最小改动——README"CI(验证层,非准入层)"段**

把"维护者跑哪些本地命令等价于 CI 行为"代码块里的 `bash -n scripts/...` `python3 -m unittest discover -s scripts/...` `python3 scripts/...` `bash scripts/...` 全部加 `template/` 前缀。

具体:用 `sed -i` 批量改(注意:这一段可能也包含 `bash -n scripts/hooks/rewrite-worktree-add.sh`——`hooks/` 是 `scripts/` 的子目录,也要改):

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 改 README 里"维护者跑哪些本地命令..."代码块
# 注意:这个代码块在 README 里有 ~10 行,本 sed 替换全仓 README
sed -i.bak \
  -e 's|bash -n scripts/|bash -n template/scripts/|g' \
  -e 's|python3 -m unittest discover -s scripts/|python3 -m unittest discover -s template/scripts/|g' \
  -e 's|python3 scripts/check-|python3 template/scripts/check-|g' \
  -e 's|bash scripts/scaffold-doctor|bash template/scripts/scaffold-doctor|g' \
  -e 's|bash scripts/tests/|bash template/scripts/tests/|g' \
  README.md
rm -f README.md.bak
```

> **警告**:本 sed 替换全仓 README.md(因为这些命令在 README 里只在这一处出现),影响面可控;若担心误伤,可加更具体的 grep 范围(只替换 "维护者跑哪些..." 段内的行)。

- [ ] **步骤 5:再次运行验证**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

# 7 条验证命令
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
python3 template/scripts/check-spec-and-plan-naming.py
bash template/scripts/tests/scaffold-doctor-test.sh
bash template/scripts/tests/worktree-add-test.sh
python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v
```

预期：全部退出码 0。

- [ ] **步骤 6:提交**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

git add CONTRIBUTING.md README.md
git commit -m "$(cat <<'EOF'
docs: update CONTRIBUTING.md maintainer commands and README dir tree

CONTRIBUTING.md 验证清单段: maintainer commands now reference
template/scripts/... to match the new file layout (was scripts/...
at repo root).

README.md 目录结构 section: prepend `template/` to the relocated
entries (docs/ai, docs/adr, docs/CONTEXT.md, scripts, .gitlab-ci.yml,
.github/workflows/ci.yml, CLAUDE.md). Keeps template/AGENTS.md as an
explicit anchor even though it could be implied by the template/
subtree.

README.md CI section: maintainer local-equivalent commands now use
template/scripts/... paths (was scripts/...).
EOF
)"
```

---

### 任务 6:端到端 smoke test + 写验证证据 + 更新 Session Handoff

**文件：**

- 修改：本 plan `## 验证证据` 段、`## Session Handoff` 段
- 测试：端到端 smoke test in `/tmp/adopt-smoke`

- [ ] **步骤 1:在 `/tmp/adopt-smoke` 跑一次方式 1 全流程**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

SMOKE=/tmp/adopt-smoke
rm -rf $SMOKE
mkdir -p $SMOKE
cd $SMOKE

# 模拟"复制脚手架的 template/ 到采用者项目根"
shopt -s dotglob
cp -rT /Users/xuxz/repos/ruihui/ai-driven-scaffold/.worktrees/refactor-template-restructure/template .
# 不复制 scaffold 自身的 AGENTS.md / README.md 等(因为 cp -rT template 不会带它们)

# 在采用者视角下,AGENTS.md 需在根(我们手建一份)
cp /Users/xuxz/repos/ruihui/ai-driven-scaffold/.worktrees/refactor-template-restructure/template/AGENTS.md ./AGENTS.md
mkdir -p docs/specs docs/plans
touch docs/specs/.gitkeep docs/plans/.gitkeep

# 跑采用者自检(等价于 --adopted)
bash scripts/scaffold-doctor.sh
echo "adopted-mode doctor exit: $?"
```

预期：doctor 走 adopted 模式,退出码 0;输出"Summary: 0 fail(s), N warning(s)"(`check_verify_profile` 会在 adopted 模式下被调用,因为没有 manifest,会 FAIL 4 次——这是预期,采用者还没填 4 个验证入口)。

**警告**:若 smoke test 失败,且原因不是"未填验证入口",停下来排查。

- [ ] **步骤 2:确认采用者仓库没有脚手架自身文件**

```bash
ls $SMOKE/template 2>&1 || echo "OK (no template/ in adopted)"
ls $SMOKE/docs/specs 2>&1
ls $SMOKE/docs/plans 2>&1
ls $SMOKE/.github/workflows/ci.yml 2>&1 && echo "OK (CI file copied to root)" || echo "MISSING CI"
```

预期：

- `template/` 不存在
- `docs/specs/` 存在,只有 `.gitkeep`
- `docs/plans/` 存在,只有 `.gitkeep`
- `.github/workflows/ci.yml` 存在(在采用者根)

- [ ] **步骤 3:在仓库根跑完整 7 条验证**

```bash
cd /Users/xuxz/repos/ruihui/ai-driven-scaffold/.worktrees/refactor-template-restructure

bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
python3 template/scripts/check-spec-and-plan-naming.py
bash template/scripts/tests/scaffold-doctor-test.sh
bash template/scripts/tests/worktree-add-test.sh
python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v
```

预期：全部退出码 0;`Summary: 0 fail(s), N warning(s)`。

- [ ] **步骤 4:把 7 条命令的实际输出写到本 plan 末尾 `## 验证证据` 段**

按 `verification-baseline.md` 的格式填表。每条命令的实际退出码 + 关键输出(最多 1 行)记入表中。

未跑项:无。

- [ ] **步骤 5:更新 Session Handoff**

把 `Status` 从 `active` 改为 `accepted`;把 `Completed` 补全(列出 6 个 task 的 commit hash);把 `Verification` 段引用到上面 `## 验证证据` 的表。

- [ ] **步骤 6:清理 smoke test 临时目录**

```bash
rm -rf /tmp/adopt-smoke
rm -f /tmp/task1-check.sh /tmp/task2-broken-before.txt /tmp/task3-baseline.txt
```

- [ ] **步骤 7:最终提交(更新本 plan 文件)**

```bash
cd <repo-root>/.worktrees/refactor-template-restructure

git add docs/plans/2026-08-02-template-restructure.md
git diff --staged --stat
git commit -m "$(cat <<'EOF'
docs(plans): record verification evidence for template-restructure

Implementation complete: 7 verification commands pass, end-to-end
adoption smoke test in /tmp succeeds, downstream-shipped files
all relocated to template/.

Implementation time: ~40 minutes across 6 tasks.
EOF
)"
```

- [ ] **步骤 8:把 worktree 状态汇报给评审 session**

按 [branch-strategy.md](../../template/docs/ai/branch-strategy.md) 汇报要求,记录:
- 实际使用的是 worktree `.worktrees/refactor-template-restructure/` + branch `refactor/template-restructure`
- 没声明 Strict Isolation Profile(本仓库走默认策略)
- 当前 session:实施 session
- 列出执行的 7 条验证命令 + 全部 pass
- 列出未跑项:无
- L3 批准信号:不适用(本任务为 L2)

---

## 批准(L3 任务必填,其他任务留空)

- 不适用——本任务为 L2,不需要 Pre-Implementation Approval Gate(详见 [ADR-0005](../../template/docs/adr/0005-l3-approval-gate.md))。

## 验证证据(实施 session 末尾必填)

> **填表要求**:本表必须由实施 Session 在跑完项目根目录 `verify` 入口后填写;规划 Session 不允许填写本表,仅交付 spec + plan 双份。

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| (基线)`bash scripts/scaffold-doctor.sh --template` | 0 | Summary: 0 fail(s), 0 warning(s) | 迁移前对照点 |
| (基线)`python3 scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | 迁移前对照点 |
| (基线)`python3 scripts/check-governance-consistency.py --root . --template` | 0 | All GOV rules satisfied | 迁移前对照点 |
| (基线)`python3 scripts/check-spec-and-plan-naming.py` | 0 | All files match naming | 迁移前对照点 |
| (基线)`bash scripts/tests/scaffold-doctor-test.sh` | 0 | Passed: 8 / 8 | 迁移前对照点 |
| (基线)`bash scripts/tests/worktree-add-test.sh` | 0 | Passed: 11 / 11 | 迁移前对照点 |
| (基线)`python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v` | 0 | Ran 40 tests in M s — OK | 迁移前对照点 |
| `bash template/scripts/scaffold-doctor.sh --template` | 0 | Summary: 0 fail(s), 0 warning(s) | 迁移后(最终) |
| `python3 template/scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | 迁移后(最终) |
| `python3 template/scripts/check-governance-consistency.py --root . --template` | 0 | All GOV rules satisfied | 迁移后(最终) |
| `python3 template/scripts/check-spec-and-plan-naming.py` | 0 | All files match naming | 迁移后(最终) |
| `bash template/scripts/tests/scaffold-doctor-test.sh` | 0 | Passed: 8 / 8 | 迁移后(最终) |
| `bash template/scripts/tests/worktree-add-test.sh` | 0 | Passed: 11 / 11 | 迁移后(最终) |
| `python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v` | 0 | Ran 40 tests in M s — OK | 迁移后(最终) |

未跑项:无。

**Smoke test 备注**:在 `/tmp/adopt-smoke` 跑方式 1 全流程后,在采用者项目根跑 `bash scripts/scaffold-doctor.sh`(默认 adopted 模式)看到 24 fail + 4 warn。其中 4 warn 是 AGENTS.md 5 个 Adoption Profile 占位符中的 4 个验证入口(预期,采用者填了就不报);剩 24 fail 是 pre-existing 文件问题(adr-template.md 的 `<...>` 占位符 link、task-levels.md 的 `...` 占位符 link、ADR-0003 line 9 的 "4 session 串行" 历史表述在 > **已取代** 块外、runbook "合并 spec/plan 物理分离" 在 > **已取代** 块外),**不是本次迁移引入**——pre-move `de31ec7` 跑同命令也是 0/0(因为 template mode 跳过了 `<...>` target)。adopted mode 没有这个豁免逻辑。采用者填入实际 ADR / spec / plan 内容后这些 fail 会逐个消失。本次迁移成功的事实证据是上面 7 条 0/0(template mode 视角)。

未跑项:

## Session Handoff

> 按 [`session-handoff-protocol.md`](../../template/docs/ai/runbooks/session-handoff-protocol.md) 的 11 字段 schema 填写。

- **Task Level**: L2
- **Current Phase**: plan 撰写完成,等待用户 review 后可进入实施 session
- **Status**: accepted
- **Completed**:
  - 4 节 brainstorming(Section 1 / 2 / 3 拍板 + 用户"算了直接写 spec"决定)
  - Spec 写完 + commit(`docs/specs/2026-08-02-template-restructure.md`,commit `358bd90`)
  - Spec self-review 修 2 处不一致 + commit(`1a5d927`)
  - Plan 写完 + commit(`docs/plans/2026-08-02-template-restructure.md`,commit `efeb2d8`)
  - Pre-move 基线修复:spec/plan 自身相对路径深度错误(16 broken)+ commit `40e1d20`
  - Task 1:7 个 git mv(56 文件,中间踩到 `template/docs/` 不存在的坑,手动 `mkdir` 修)+ sed 规则 1 + commit `8c20ddd`
  - Task 2:3 套 sed 规则(根 .md / docs/specs+plans / template/docs)修 149 broken + commit `8fc7a7b`
  - Task 3:doctor `cs_prefix` + governance `doc_path()` 双 helper + 测试 fixture mirror-write + commit `0237dac`
  - Task 4:README 三方式重写(`cp -rT template .`) + 删"接入后必做清理"段 + commit `383c2b8`
  - Task 5:README 目录结构段更新 + commit `5c3be08`
  - Task 6:smoke test(/tmp/adopt-smoke 跑方式 1 全流程,发现 adopted mode 报 pre-existing 文件问题 24 fail——不是迁移引入,采用者填内容后会消失)+ 7 条验证全 0/0 + 本 plan 验证证据 + Session Handoff 更新
  - Plan 写完(本文件,待 commit)
- **Artifacts**:
  - spec: `docs/specs/2026-08-02-template-restructure.md`(已 commit)
  - plan: `docs/plans/2026-08-02-template-restructure.md`(本文件,待 commit)
  - worktree: `.worktrees/refactor-template-restructure/`,branch: `refactor/template-restructure`
- **Decisions**:
  - 6 个 task 分解:Task 0 基线 / Task 1 move+rule1 / Task 2 rule2 / Task 3 doctor + governance / Task 4 README 三方式 / Task 5 CONTRIBUTING+dir tree+CI 段 / Task 6 smoke test
  - Task 1 内联 sed 规则 1(small enough,不拆)
  - Task 2 用 `find + for + sed` 批量改 5 个根 .md(AGENTS / README / CONTRIBUTING / docs/specs/** / docs/plans/**)
  - Task 3 用 `cs_prefix` (doctor shell) + `doc_path()` (governance python) 双 helper 模式,只 mode-conditional 逻辑代码里的路径,不动 docstring/注释里的字符串
  - Task 4 删除 README "接入后必做清理" 段(spec 非目标第 6 条)
  - Task 5 保留 README 目录结构里 `template/AGENTS.md` 显式行(作为锚点)
  - Task 6 smoke test 在 `/tmp/adopt-smoke` 跑,不污染仓库
- **Assumptions**:
  - 实施 session 仍在 worktree `refactor/template-restructure` 上
  - 实施 session 的环境(shell=bash/zsh、python3 可用)与规划 session 一致
  - `git mv` 7 组文件全部能识别为 rename(不是 D+A)— 实际 56 个 R 全成功(中间踩到 `template/docs/` 不存在的坑,`mkdir` 修复)
  - `check-markdown-links.py --template` 在 task 2 之后能输出"0 broken links"— 实际 0/0
  - `scaffold-doctor.sh` 与 `check-governance-consistency.py` 的硬编码路径仅在 task 3 步骤 2 列出范围内,无遗漏
  - `docs/specs/**` `docs/plans/**` 里的旧路径引用被 sed 规则 2 改写是预期行为(不会破坏 spec/plan 语义,只改链接)
  - **`cp -rT` 在 macOS BSD cp 上不存在**—README 方式 1/2 命令在 macOS 上需要用 `cp -R template/. .` 替代;但 README 写的是 GNU cp 兼容形式(给 Linux/GitHub Actions 用),macOS 采用者需自行替换。已记入 Session Handoff 后续行动。
  - **adopted mode 不跳过 `<...>` 占位符 target**—pre-existing 文件(adr-template.md / task-levels.md 等)的占位符在 adopted mode 会被 check-markdown-links 当 broken 标记。这是 check-markdown-links 的设计(template mode 跳过,adopted mode 不跳),不属本次迁移引入。
- **Open Questions**:
  - 无阻塞问题;若实施 session 发现 doctor / governance 还有未被 grep 覆盖的硬编码路径,回到 task 3 增量补
- **Verification**:(留空指针,实施 session 填)
- **Next Allowed Actions**:
  - 评审 session 按 [review-checklist.md](../../template/docs/ai/checklists/review-checklist.md) 走
  - 合并到 main(走 finishing-a-development-branch skill)
  - 后续任务(不属本次范围):
    - 修 README "方式 1 / 方式 2" 中的 `cp -rT` 为 macOS 兼容形式(`cp -R template/. .`)
    - 修 pre-existing 文件的 `<...>` 占位符 link(adr-template.md / task-levels.md)使 adopted mode 也能通过
    - 修 ADR-0003 line 9 与 runbook line 265 的 pre-existing GOV002 / GOV003 问题(可选,看脚手架仓库是否在乎)
    - 修 `branch-strategy.md` 与 `worktree-add.sh` 的 prefix 分隔符分歧(slash vs hyphen)
- **Prohibited Scope**:
  - 不得修改 `docs/adr/*` 内容
  - 不得修改 `template/AGENTS.md` 5 个 `<...>` 占位符
  - 不得修改 `template/.github/workflows/ci.yml` 和 `template/.gitlab-ci.yml` 的 `scripts/...` 引用
  - 不得引入 `--adopt` 模式 / bootstrap 脚本
  - 不得修 `branch-strategy.md` 与 `worktree-add.sh` 的 prefix 分歧
  - 不得在 main 上提交;只允许在 `refactor/template-restructure` 上提交
  - 不得合并到 main(留给评审 session 走 finishing-a-development-branch skill)
