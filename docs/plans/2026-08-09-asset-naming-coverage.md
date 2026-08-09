# 资产命名覆盖与路径基准实施计划

> 基于 spec：[docs/specs/2026-08-09-asset-naming-coverage.md](../specs/2026-08-09-asset-naming-coverage.md)

## 元信息

- 主题：naming, task-packet, template, monorepo, doctor
- 状态：draft
- 关联 ADR：ADR-0004

> 命名规范见 [../spec-and-plan-naming.md](../../template/docs/ai/spec-and-plan-naming.md);文件名前缀为 `<date>-<name>.md`。

> **面向 Agent 执行者:** 步骤使用复选框 `- [ ]` 语法跟踪;按手工清单逐任务执行,保持逐任务验证纪律。

**任务概述(限 2-3 句,本字段仅说「做什么/分几步」):** 把 task-packets 纳入命名检查与 doctor 链路,给 template 补空目录占位与接入清单条目,并在命名规范里声明路径基准与 monorepo 规则。分 8 个任务,前 3 个改脚本(TDD),后 4 个改文档/模板,末任务全量 verify。

---

## 文件清单

- 新建:`template/docs/specs/.gitkeep`、`template/docs/plans/.gitkeep`、`template/docs/task-packets/.gitkeep`
- 修改:`template/scripts/check-spec-and-plan-naming.py`、`template/scripts/tests/test_check_spec_and_plan_naming.py`、`template/scripts/scaffold-doctor.sh`、`template/docs/ai/spec-and-plan-naming.md`、`template/docs/ai/templates/task-packet.md`、`template/docs/ai/checklists/adoption-checklist.md`
- 测试:`template/scripts/tests/test_check_spec_and_plan_naming.py`、`bash template/scripts/scaffold-doctor.sh --template`

> 所有路径相对于仓库根。worktree 路径:`.worktrees/docs-asset-naming-coverage/`。实施时在 worktree 内操作,提交到 `docs-asset-naming-coverage` 分支。

### 任务 1:命名检查覆盖 task-packets(TDD)

**文件:**

- 修改:`template/scripts/tests/test_check_spec_and_plan_naming.py`(新增 task-packets 用例)
- 修改:`template/scripts/check-spec-and-plan-naming.py`(`TARGET_DIRS` + docstring)

**Interfaces:**

- Consumes:无前置任务
- Produces:`check-spec-and-plan-naming.py` 的 `TARGET_DIRS` 含 `"docs/task-packets"`;测试覆盖 task-packets 合法 / 非法

- [ ] **步骤 1:编写失败测试**

在 `template/scripts/tests/test_check_spec_and_plan_naming.py` 的 `TestCheckSpecAndPlanNaming` 类中,在 `test_valid_names_return_zero` 方法后新增两个用例:

```python
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
```

- [ ] **步骤 2:运行测试,确认失败**

从仓库根执行:

```bash
python3 -m pytest template/scripts/tests/test_check_spec_and_plan_naming.py -v
```

预期:`test_valid_task_packets_return_zero` 与 `test_invalid_task_packets_return_one` FAIL(因为 `TARGET_DIRS` 不含 `docs/task-packets`,脚本跳过该目录,合法用例返回 0 但非法用例因未扫到也返回 0,断言 `returncode == 1` 失败)。

- [ ] **步骤 3:实现最小改动**

`template/scripts/check-spec-and-plan-naming.py`:

(a) 顶部 docstring 第 2 行:

```python
"""check-spec-and-plan-naming.py — docs/specs / docs/plans / docs/task-packets 命名只读检查器

仅校验 ``<root>/docs/specs/*.md`` 与 ``<root>/docs/plans/*.md`` 与 ``<root>/docs/task-packets/*.md`` 的直接子级
文件名是否匹配 ``<YYYY-MM-DD>-<kebab-name>.md``：
```

(b) `TARGET_DIRS` 常量:

```python
TARGET_DIRS = ("docs/specs", "docs/plans", "docs/task-packets")
```

- [ ] **步骤 4:再次运行验证**

```bash
python3 -m pytest template/scripts/tests/test_check_spec_and_plan_naming.py -v
```

预期:全部 PASS(含两个新用例)。同时跑端到端扫描确认本仓库既有文件仍合法:

```bash
python3 template/scripts/check-spec-and-plan-naming.py --root .
```

预期:退出码 0,无输出。

- [ ] **步骤 5:提交**

```bash
git add template/scripts/check-spec-and-plan-naming.py template/scripts/tests/test_check_spec_and_plan_naming.py
git commit -m "feat(scripts): cover docs/task-packets in naming checker"
```

---

### 任务 2:doctor 增加 task-packets 存在性检查

**文件:**

- 修改:`template/scripts/scaffold-doctor.sh`

**Interfaces:**

- Consumes:任务 1(TARGET_DIRS 已含 task-packets,但本任务不依赖脚本检查,仅查目录存在性;可与任务 1 解耦)
- Produces:doctor 的 `check_structure` 输出 `docs/task-packets` PASS/FAIL 行

- [ ] **步骤 1:编写失败检查**

在 worktree 内,临时构造缺 task-packets 的场景验证现状 doctor 不报:

```bash
cd "$(git rev-parse --show-toplevel)"
# 现状:仓库根有 docs/task-packets,doctor 不查它;template/docs 下无 task-packets
bash template/scripts/scaffold-doctor.sh --template | grep task-packets || echo "no task-packets line (expected before fix)"
```

预期:输出 `no task-packets line (expected before fix)`(现状不查 task-packets)。

- [ ] **步骤 2:运行检查,确认当前状态**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:全 PASS,退出 0(基线干净,但缺 task-packets 检查项)。

- [ ] **步骤 3:实现最小改动**

`template/scripts/scaffold-doctor.sh` 的 `check_structure()` 函数中,在 `docs/plans` 检查块之后插入 task-packets 检查:

```sh
  if [ -d docs/plans ]; then
    pass 'docs/plans exists'
  else
    fail 'docs/plans is missing'
  fi
  if [ -d docs/task-packets ]; then
    pass 'docs/task-packets exists'
  else
    fail 'docs/task-packets is missing'
  fi
```

同时更新文件顶部注释第 5 行的 `check_structure` 摘要,把 `docs/specs / docs/plans` 改为 `docs/specs / docs/plans / docs/task-packets`:

```sh
#   check_structure        AGENTS.md / Adoption Profile / docs/specs / docs/plans
#                          / docs/task-packets / ADR status / CI placeholders
```

- [ ] **步骤 4:再次运行验证**

```bash
bash template/scripts/scaffold-doctor.sh --template | grep task-packets
```

预期:输出 `PASS docs/task-packets exists`(仓库根 `docs/task-packets` 存在)。

构造缺失场景验证 FAIL 路径:

```bash
tmpdir=$(mktemp -d); mkdir -p "$tmpdir/docs/specs" "$tmpdir/docs/plans"
bash template/scripts/scaffold-doctor.sh --adopted "$tmpdir" | grep task-packets
rm -rf "$tmpdir"
```

预期:输出 `FAIL docs/task-packets is missing`。

- [ ] **步骤 5:提交**

```bash
git add template/scripts/scaffold-doctor.sh
git commit -m "feat(scripts): doctor checks docs/task-packets existence"
```

---

### 任务 3:doctor 接入命名检查

**文件:**

- 修改:`template/scripts/scaffold-doctor.sh`

**Interfaces:**

- Consumes:任务 1(`check-spec-and-plan-naming.py` 已覆盖三目录)
- Produces:doctor 调用 `check-spec-and-plan-naming.py`,违例计入退出码

- [ ] **步骤 1:编写失败检查**

```bash
# 现状:doctor 不调用 naming check
bash template/scripts/scaffold-doctor.sh --template | grep -i naming || echo "no naming check line (expected before fix)"
```

预期:`no naming check line`。

- [ ] **步骤 2:运行检查,确认当前状态**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:全 PASS,退出 0。

- [ ] **步骤 3:实现最小改动**

`template/scripts/scaffold-doctor.sh`:

(a) 在解析 `checker_consistency` 那行之后,新增 naming checker 路径变量:

```sh
checker_links="$script_dir/check-markdown-links.py"
checker_consistency="$script_dir/check-governance-consistency.py"
checker_naming="$script_dir/check-spec-and-plan-naming.py"
```

(b) 在 `check_consistency()` 函数之后、`check_verify_profile()` 之前,新增 `check_naming()` 函数:

```sh
# =========================================================================
# check_naming — delegates to python3 scripts/check-spec-and-plan-naming.py
# Validates <YYYY-MM-DD>-<kebab-name>.md for docs/specs / docs/plans /
# docs/task-packets direct children. Missing python3 → WARN (no hard fail).
# =========================================================================
check_naming() {
  if [ ! -f "$checker_naming" ]; then
    warn "naming checker script missing: $checker_naming"
    return
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not available; skipping naming check"
    return
  fi

  cn_out=$(python3 "$checker_naming" --root "$abs_root" 2>&1)
  cn_rc=$?
  if [ "$cn_rc" -eq 0 ]; then
    pass 'spec/plan/task-packet naming clean'
    return
  fi
  if [ "$cn_rc" -eq 2 ]; then
    fail "naming checker parameter error: $cn_out"
    return
  fi

  # rc == 1: emit one FAIL per non-empty finding line
  cn_emitted=0
  while IFS= read -r cn_line; do
    [ -n "$cn_line" ] || continue
    fail "naming violation: $cn_line"
    cn_emitted=$((cn_emitted + 1))
  done <<EOF
$cn_out
EOF
  if [ "$cn_emitted" -eq 0 ]; then
    fail "naming checker exited 1 with no findings"
  fi
}
```

(c) 在文件末尾的调用块,`check_consistency` 之后加 `check_naming`(两种模式都调用):

```sh
# --- run all checks ---
check_structure
check_links
check_consistency
check_naming
if [ "$mode" = adopted ]; then
  check_verify_profile
fi
```

(d) 更新顶部注释 `Usage` 上方的汇总注释,把 naming 加入四类变五类(可选,保持准确):

```sh
# Aggregates five categories of read-only checks:
#   check_structure        AGENTS.md / Adoption Profile / docs/specs / docs/plans
#                          / docs/task-packets / ADR status / CI placeholders
#   check_links            python3 scripts/check-markdown-links.py [--template]
#   check_consistency      python3 scripts/check-governance-consistency.py [--template]
#   check_naming           python3 scripts/check-spec-and-plan-naming.py
#   check_verify_profile   adopted mode only: verify entry in common manifests
```

- [ ] **步骤 4:再次运行验证**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:含 `PASS spec/plan/task-packet naming clean`,退出 0。

构造命名违例验证 FAIL 路径:

```bash
tmpdir=$(mktemp -d); mkdir -p "$tmpdir/docs/specs"
echo x > "$tmpdir/docs/specs/bad.md"
bash template/scripts/scaffold-doctor.sh --adopted "$tmpdir" | grep -E "naming violation|naming clean"
rm -rf "$tmpdir"
```

预期:输出含 `FAIL naming violation: docs/specs/bad.md`。

- [ ] **步骤 5:提交**

```bash
git add template/scripts/scaffold-doctor.sh
git commit -m "feat(scripts): doctor invokes spec/plan naming checker"
```

---

### 任务 4:spec-and-plan-naming.md 扩适用范围 + 路径基准段

**文件:**

- 修改:`template/docs/ai/spec-and-plan-naming.md`

**Interfaces:**

- Consumes:无
- Produces:命名规范覆盖 task-packets;新增"路径基准"小节

- [ ] **步骤 1:编写失败检查**

```bash
rg -n "task-packets" template/docs/ai/spec-and-plan-naming.md || echo "no task-packets in naming spec (expected before fix)"
rg -n "路径基准" template/docs/ai/spec-and-plan-naming.md || echo "no path-basis section (expected before fix)"
```

预期:两条 `no ...` 输出。

- [ ] **步骤 2:运行检查,确认当前状态**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:全 PASS(文档改动前基线干净)。

- [ ] **步骤 3:实现最小改动**

`template/docs/ai/spec-and-plan-naming.md`:

(a) "适用范围"段,在现有两条后加第三条:

```markdown
## 适用范围

- `docs/specs/<date>-<name>.md`
- `docs/plans/<date>-<name>.md`
- `docs/task-packets/<date>-<name>.md`

> **适用差异**:命名格式(下文)三类资产统一;`## 元信息` 段与状态机**仅 spec / plan 必填**,task-packet 是一次性 L1 资产,不适用元信息段与状态机(详见各自模板)。

设计原则参见 [ADR-0004](../adr/0004-l2-spec-and-plan.md);本文档落地 ADR-0004 中未约束的命名细节与元信息字段。
```

(b) 在"文件命名"大段之前(即"适用范围"之后),新增"路径基准"小节:

```markdown
## 路径基准

- `docs/specs`、`docs/plans`、`docs/task-packets` 路径**相对于项目根**。
- monorepo:改动落在单个子包时,spec / plan / task-packet 放 `<pkg>/docs/specs/`;跨包 L2 放仓库根 `docs/specs/`。
- 命名检查脚本支持子包场景:`python3 scripts/check-spec-and-plan-naming.py --root <pkg>`;doctor 默认查根,子包项目在各包内运行。
```

(c) "元信息段(顶部必填)"段的标题与首行加适用对象限定,把:

```markdown
## 元信息段(顶部必填)

每个 spec / plan 文件**必须在正文之前**含 `## 元信息` 段,顺序固定:
```

改为:

```markdown
## 元信息段(顶部必填,仅 spec / plan)

每个 spec / plan 文件**必须在正文之前**含 `## 元信息` 段,顺序固定;task-packet 不适用本段:
```

(d) "状态机"段标题加适用对象限定,把:

```markdown
## 状态机
```

改为:

```markdown
## 状态机(仅 spec / plan)
```

- [ ] **步骤 4:再次运行验证**

```bash
rg -n "task-packets" template/docs/ai/spec-and-plan-naming.md
rg -n "路径基准" template/docs/ai/spec-and-plan-naming.md
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:前两条有命中;doctor 全 PASS 退出 0(无 broken link)。

- [ ] **步骤 5:提交**

```bash
git add template/docs/ai/spec-and-plan-naming.md
git commit -m "docs(ai): extend naming spec to task-packets + path basis section"
```

---

### 任务 5:task-packet.md 模板顶部加命名规范链接

**文件:**

- 修改:`template/docs/ai/templates/task-packet.md`

**Interfaces:**

- Consumes:任务 4(命名规范已覆盖 task-packets)
- Produces:task-packet 模板指向命名规范

- [ ] **步骤 1:编写失败检查**

```bash
rg -n "spec-and-plan-naming" template/docs/ai/templates/task-packet.md || echo "no naming link (expected before fix)"
```

预期:`no naming link`。

- [ ] **步骤 2:运行检查,确认当前状态**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:全 PASS。

- [ ] **步骤 3:实现最小改动**

`template/docs/ai/templates/task-packet.md` 顶部第一个 blockquote(以 `> **L2+ 批量协作时**` 开头)之前,新增一行命名规范引用:

```markdown
> 命名遵循 [spec-and-plan-naming.md](../spec-and-plan-naming.md) 的 `<YYYY-MM-DD>-<kebab-name>.md` 格式;task-packet 不适用 `## 元信息` 段与状态机。

> **L2+ 批量协作时**（把一次实施拆给多个 worker agent 并行落地），本模板的"8 个批量子字段"……
```

- [ ] **步骤 4:再次运行验证**

```bash
rg -n "spec-and-plan-naming" template/docs/ai/templates/task-packet.md
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:有命中;doctor 全 PASS(链接 `../spec-and-plan-naming.md` 相对 `templates/` 解析到 `ai/spec-and-plan-naming.md`,合法)。

- [ ] **步骤 5:提交**

```bash
git add template/docs/ai/templates/task-packet.md
git commit -m "docs(templates): link task-packet template to naming spec"
```

---

### 任务 6:template 补空目录占位

**文件:**

- 新建:`template/docs/specs/.gitkeep`、`template/docs/plans/.gitkeep`、`template/docs/task-packets/.gitkeep`

**Interfaces:**

- Consumes:无
- Produces:三个空目录占位文件

- [ ] **步骤 1:编写失败检查**

```bash
ls template/docs/specs template/docs/plans template/docs/task-packets 2>&1 | head
```

预期:`No such file or directory`(三个目录均不存在)。

- [ ] **步骤 2:运行检查,确认当前状态**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:全 PASS( doctor 查根 `docs/specs` 等,不查 `template/docs/specs`,故不受影响)。

- [ ] **步骤 3:实现最小改动**

```bash
mkdir -p template/docs/specs template/docs/plans template/docs/task-packets
: > template/docs/specs/.gitkeep
: > template/docs/plans/.gitkeep
: > template/docs/task-packets/.gitkeep
```

- [ ] **步骤 4:再次运行验证**

```bash
ls template/docs/specs/.gitkeep template/docs/plans/.gitkeep template/docs/task-packets/.gitkeep
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:三个文件存在;doctor 全 PASS。

- [ ] **步骤 5:提交**

```bash
git add template/docs/specs/.gitkeep template/docs/plans/.gitkeep template/docs/task-packets/.gitkeep
git commit -m "feat(template): add empty specs/plans/task-packets dir placeholders"
```

---

### 任务 7:adoption-checklist 补复制清单与检查项

**文件:**

- 修改:`template/docs/ai/checklists/adoption-checklist.md`

**Interfaces:**

- Consumes:任务 6(template 带空目录)、任务 2(doctor 查 task-packets)
- Produces:接入清单含 task-packets 复制条目与检查项

- [ ] **步骤 1:编写失败检查**

```bash
rg -n "task-packets" template/docs/ai/checklists/adoption-checklist.md || echo "no task-packets in checklist (expected before fix)"
```

预期:`no task-packets`。

- [ ] **步骤 2:运行检查,确认当前状态**

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:全 PASS。

- [ ] **步骤 3:实现最小改动**

`template/docs/ai/checklists/adoption-checklist.md`:

(a) "人工检查"段中,把:

```markdown
- [ ] `docs/specs/` 和 `docs/plans/` 存在，用于承接 L2+ 任务交付物。
```

改为:

```markdown
- [ ] `docs/specs/`、`docs/plans/`、`docs/task-packets/` 存在，用于承接 L1 task-packet 与 L2+ spec/plan 交付物（可从 `template/docs/` 下对应空目录复制，或 `mkdir -p`）。
```

(b) "使用时机"段第二条,把:

```markdown
- 既有项目复制 `AGENTS.md`、`docs/ai/`、`docs/adr/` 后。
```

改为:

```markdown
- 既有项目复制 `AGENTS.md`、`docs/ai/`、`docs/adr/`，并补建 `docs/specs/`、`docs/plans/`、`docs/task-packets/`（可从 `template/docs/` 复制空目录）后。
```

- [ ] **步骤 4:再次运行验证**

```bash
rg -n "task-packets" template/docs/ai/checklists/adoption-checklist.md
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
```

预期:有命中;doctor 全 PASS。

- [ ] **步骤 5:提交**

```bash
git add template/docs/ai/checklists/adoption-checklist.md
git commit -m "docs(checklists): add task-packets to adoption checklist"
```

---

### 任务 8:全量 verify + Session Handoff 回填

**文件:**

- 修改:`docs/plans/2026-08-09-asset-naming-coverage.md`(回填验证证据 + Session Handoff)
- 修改:`docs/specs/2026-08-09-asset-naming-coverage.md`(状态 draft → accepted,如全部命中)

**Interfaces:**

- Consumes:任务 1–7 全部完成
- Produces:验证证据表 + Session Handoff 回填

- [ ] **步骤 1:跑全量 verify**

从仓库根(worktree 根)执行:

```bash
bash template/scripts/scaffold-doctor.sh --template; echo "exit:$?"
python3 -m pytest template/scripts/tests/ -v
python3 template/scripts/check-spec-and-plan-naming.py --root .
```

- [ ] **步骤 2:确认结果**

预期:doctor 退出 0(0 fail);pytest 全过(含新增 task-packets 用例);naming check 退出 0 无输出。

- [ ] **步骤 3:回填 plan 验证证据段**

把上方三条命令的实际退出码与关键输出摘要填入本 plan 的 `## 验证证据` 段表格。

- [ ] **步骤 4:回填 Session Handoff**

按 11 字段 schema 回填本 plan 末尾 `## Session Handoff`。

- [ ] **步骤 5:更新 spec 状态**

如验收标准全部命中,把 `docs/specs/2026-08-09-asset-naming-coverage.md` 的 `## 元信息` 段 `状态:draft` 改为 `状态:accepted`。

- [ ] **步骤 6:提交**

```bash
git add docs/plans/2026-08-09-asset-naming-coverage.md docs/specs/2026-08-09-asset-naming-coverage.md
git commit -m "docs: fill verify evidence + accept asset-naming-coverage spec"
```

---

## 批准(L3 任务必填,其他任务留空)

本任务为 L2,无 L3 批准段。

## 验证证据(实施 session 末尾必填)

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `bash template/scripts/scaffold-doctor.sh --template` | 0 | 14 PASS, 0 fail, 0 warn;含 `docs/task-packets exists` + `spec/plan/task-packet naming clean` | 完整验证入口(ADR-0002)
| `python3 -m unittest discover -s template/scripts/tests -p "test_*.py"` | 0 | Ran 42 tests OK | 含新增 `test_valid_task_packets_return_zero` / `test_invalid_task_packets_return_one`
| `python3 template/scripts/check-spec-and-plan-naming.py --root .` | 0 | 无输出 | 三目录(specs/plans/task-packets)命名均合法
| `bash template/scripts/scaffold-doctor.sh --adopted $tmp`(缺 task-packets) | 1 | `FAIL docs/task-packets is missing` | 验收:缺目录 FAIL 路径
| `bash template/scripts/scaffold-doctor.sh --adopted $tmp`(task-packets 非法命名) | 1 | `FAIL naming violation: docs/task-packets/bad.md` | 验收:命名违例 FAIL 路径

未跑项:无(pytest 未装,改用标准库 `python3 -m unittest` 等价覆盖,42 项全过)

## Session Handoff

- Task Level: L2
- Current Phase: implementation complete, awaiting final whole-branch review
- Status: accepted
- Completed: spec + plan(规划 session)+ 任务 1–7 实施(subagent-driven,逐任务 review clean)+ 任务 8 verify 回填
- Artifacts: `docs/specs/2026-08-09-asset-naming-coverage.md`(状态已转 accepted)、`docs/plans/2026-08-09-asset-naming-coverage.md`
- Commits: `0862b68`(spec+plan) → `3bdef36`(T1) → `760634e`(T2) → `e1316ad`(T3) → `b3cead6`(T4) → `b26d415`(T5) → `d18d0fb`(T6) → `9b4548b`(T7)
- Decisions: 不改名 spec-and-plan-naming.md(外科优先);命名检查接入 doctor;路径基准走纯文档方案 C;不给 task-packet 加元信息段/状态机;doctor 接入 naming check 时 python3 缺失降级 WARN 不硬失败;pytest 缺失改用 stdlib unittest 等价覆盖
- Assumptions(已验证): 本仓库既有 specs/plans/task-packets 命名均合法(接入 naming check 后基线 0 fail);adopted 项目复制 scripts/ 目录(既有约定,doctor 已依赖 check-markdown-links.py 等)
- Open Questions: 无
- Minor findings(留 final review triage): 任务 4 路径基准段 `--root <pkg>` 用尖括号占位符,建议改反引号写法避免与占位符语义混淆
- Verification: `scaffold-doctor.sh --template` exit 0(14 PASS,含 `docs/task-packets exists` + `spec/plan/task-packet naming clean`);`python3 -m unittest` 42 项 OK;naming check exit 0
- Next Allowed Actions: 最终整支 review → 决定合并到 main / PR
- Prohibited Scope: 不改名 spec-and-plan-naming.md;不加 Adoption Profile 的 Spec Root 字段;不让 doctor 自动 mkdir;不改 feature-spec.md / implementation-plan.md 模板结构
