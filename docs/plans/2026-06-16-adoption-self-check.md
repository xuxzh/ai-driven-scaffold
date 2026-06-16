# Adoption Self-Check 实施计划

> **基于 spec**：[docs/specs/2026-06-16-adoption-self-check.md](../specs/2026-06-16-adoption-self-check.md)
> （此行**必填**，否则视为与 spec 失联，详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)）

> **面向 Agent 执行者：** 步骤使用复选框 `- [ ]` 语法跟踪；如当前会话支持多 agent 调度，可拆给子 agent；否则按手工清单逐任务执行，并保持同样的逐任务验证纪律。

**目标：** 为脚手架新增接入自检能力：人工 checklist + 只读 `scripts/scaffold-doctor.sh` + README / CONTRIBUTING 接入说明。

**实现方式：** 文档仍作为治理源头；doctor 脚本只读检查接入状态并输出 `PASS` / `WARN` / `FAIL`，不自动修改任何文件。

**技术栈：** Markdown + POSIX shell；不引入项目运行时依赖。

---

## 文件清单

- 新建：
  - `docs/ai/checklists/adoption-checklist.md`
  - `scripts/scaffold-doctor.sh`
- 修改：
  - `README.md`
  - `CONTRIBUTING.md`
- 测试：
  - `bash -n scripts/scaffold-doctor.sh`
  - `bash scripts/scaffold-doctor.sh`
  - `rg -n '<[^>]+>' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md scripts/scaffold-doctor.sh`
  - `rg -n 'adoption-checklist|scaffold-doctor' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md`

## 非目标

- 不自动替换占位符。
- 不生成或修改 manifest。
- 不把 doctor 接入 CI、hooks 或 PR 模板作为强门禁。
- 不修改 ADR 状态；doctor 只报告 ADR 状态与硬约束表述之间的潜在冲突。

### 任务 1：新增接入 checklist

**文件：**

- 新建：`docs/ai/checklists/adoption-checklist.md`
- 修改：无
- 测试：`rg -n 'scaffold-doctor|verify|占位符|ADR' docs/ai/checklists/adoption-checklist.md`

- [ ] **步骤 1：创建 checklist 文档**

创建 `docs/ai/checklists/adoption-checklist.md`，内容如下：

```markdown
# 接入自检清单

> 本清单用于确认脚手架已经正确接入目标项目。它检查的是"治理脚手架是否可用"，不替代项目自身的 `verify`。

## 使用时机

- 新项目从模板创建后。
- 既有项目复制 `AGENTS.md`、`docs/ai/`、`docs/adr/` 后。
- 修改脚手架接入规则、CI 模板或项目元信息后。

## 人工检查

- [ ] `AGENTS.md` 存在，并且用户项目元信息已按项目实际情况填写。
- [ ] `AGENTS.md` 不再保留必填占位符：`<pm>`、`<app-dir>`、`<entry-file>`、`<shared-dir>`、`<test-dir>`。
- [ ] 项目 manifest 中存在 `verify` 入口，且该入口能覆盖当前项目的 lint、typecheck、test、build 需求。
- [ ] `docs/specs/` 和 `docs/plans/` 存在，用于承接 L2+ 任务交付物。
- [ ] 如启用 `.github/workflows/ci.yml` 或 `.gitlab-ci.yml`，其中的 `<...>` 占位符已经替换或删除。
- [ ] ADR-0002 / 0003 / 0004 / 0005 的状态与 `AGENTS.md` 中"硬约束依据"的表述一致。

## 脚本检查

从仓库根目录运行：

```bash
bash scripts/scaffold-doctor.sh
```

结果含义：

| 标记 | 含义 |
|---|---|
| `PASS` | 检查项满足预期 |
| `WARN` | 需要人工判断，但不阻塞脚本退出码 |
| `FAIL` | 接入缺失或明显不可用，脚本退出码为 `1` |

## 边界

- doctor 只读文件，不自动修复。
- doctor 只检查脚手架接入状态，不证明业务代码正确。
- doctor 通过后，L1+ 任务仍必须按 `verification-baseline.md` 运行项目 `verify`。
```

- [ ] **步骤 2：检查 checklist 关键词**

执行：

```bash
rg -n 'scaffold-doctor|verify|占位符|ADR' docs/ai/checklists/adoption-checklist.md
```

预期：

```text
命中脚本名称、verify 边界、占位符和 ADR 状态相关段落。
```

- [ ] **步骤 3：提交 checklist 切片**

执行：

```bash
git status --short
git add docs/ai/checklists/adoption-checklist.md
git commit -m "docs(ai): add adoption self-check checklist"
```

预期：

```text
仅暂存并提交 adoption checklist。
```

### 任务 2：新增只读 scaffold doctor

**文件：**

- 新建：`scripts/scaffold-doctor.sh`
- 修改：无
- 测试：
  - `bash -n scripts/scaffold-doctor.sh`
  - `bash scripts/scaffold-doctor.sh`

- [ ] **步骤 1：创建脚本目录和 doctor 脚本**

创建 `scripts/scaffold-doctor.sh`，内容如下：

```sh
#!/bin/sh

set -u

fail_count=0
warn_count=0

pass() {
  printf 'PASS %s\n' "$1"
}

warn() {
  warn_count=$((warn_count + 1))
  printf 'WARN %s\n' "$1"
}

fail() {
  fail_count=$((fail_count + 1))
  printf 'FAIL %s\n' "$1"
}

file_contains() {
  file=$1
  pattern=$2

  [ -f "$file" ] && grep -Eq "$pattern" "$file"
}

check_agents_md() {
  if [ ! -f AGENTS.md ]; then
    fail 'AGENTS.md is missing'
    return
  fi

  pass 'AGENTS.md exists'

  if grep -Eq '<(pm|app-dir|entry-file|shared-dir|test-dir)>' AGENTS.md; then
    fail 'AGENTS.md still contains required project metadata placeholders'
  else
    pass 'AGENTS.md required project metadata placeholders are filled'
  fi
}

check_l2_dirs() {
  if [ -d docs/specs ]; then
    pass 'docs/specs exists'
  else
    fail 'docs/specs is missing'
  fi

  if [ -d docs/plans ]; then
    pass 'docs/plans exists'
  else
    fail 'docs/plans is missing'
  fi
}

check_verify_entry() {
  found_manifest=0
  found_verify=0

  for manifest in package.json pyproject.toml Cargo.toml go.mod mix.exs Makefile justfile Taskfile.yml Taskfile.yaml; do
    if [ -f "$manifest" ]; then
      found_manifest=1
      if grep -Eq '(^|["._ -])verify([":._ -]|$)' "$manifest"; then
        found_verify=1
      fi
    fi
  done

  if [ "$found_manifest" -eq 0 ]; then
    warn 'no common project manifest found; verify entry could not be detected'
    return
  fi

  if [ "$found_verify" -eq 1 ]; then
    pass 'verify entry detected in a common manifest'
  else
    fail 'no verify entry detected in common manifests'
  fi
}

check_ci_placeholders() {
  found_ci=0

  for ci_file in .github/workflows/ci.yml .gitlab-ci.yml; do
    if [ -f "$ci_file" ]; then
      found_ci=1
      if grep -Eq '<[^>]+>' "$ci_file"; then
        warn "$ci_file still contains angle-bracket placeholders"
      else
        pass "$ci_file has no angle-bracket placeholders"
      fi
    fi
  done

  if [ "$found_ci" -eq 0 ]; then
    warn 'no bundled CI template found'
  fi
}

check_adr_status() {
  missing_constraint=0

  for adr_id in ADR-0002 ADR-0003 ADR-0004 ADR-0005; do
    if ! file_contains AGENTS.md "$adr_id"; then
      missing_constraint=1
    fi
  done

  if [ "$missing_constraint" -eq 1 ]; then
    warn 'AGENTS.md does not reference all ADR-0002 through ADR-0005 hard constraints'
  fi

  for adr in \
    docs/adr/0002-verify-hard-gate.md \
    docs/adr/0003-multi-session-l2.md \
    docs/adr/0004-l2-spec-and-plan.md \
    docs/adr/0005-l3-approval-gate.md
  do
    if [ ! -f "$adr" ]; then
      fail "$adr is missing"
      continue
    fi

    status=$(awk '
      /^## 状态$/ { in_status = 1; next }
      in_status && NF { print; exit }
    ' "$adr")

    case "$status" in
      Proposed*)
      warn "$adr is Proposed while AGENTS.md treats it as a hard constraint"
      ;;
      *)
      pass "$adr status is not Proposed"
      ;;
    esac
  done
}

check_agents_md
check_l2_dirs
check_verify_entry
check_ci_placeholders
check_adr_status

printf '\nSummary: %s fail(s), %s warning(s)\n' "$fail_count" "$warn_count"

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi

exit 0
```

- [ ] **步骤 2：运行 shell 语法检查**

执行：

```bash
bash -n scripts/scaffold-doctor.sh
```

预期：

```text
无输出，退出码 0。
```

- [ ] **步骤 3：运行 doctor，确认当前模板仓库报告预期问题**

执行：

```bash
bash scripts/scaffold-doctor.sh
```

预期：

```text
输出至少包含：
- PASS AGENTS.md exists
- FAIL AGENTS.md still contains required project metadata placeholders
- PASS docs/specs exists
- PASS docs/plans exists
- WARN .github/workflows/ci.yml still contains angle-bracket placeholders
- WARN .gitlab-ci.yml still contains angle-bracket placeholders
- WARN docs/adr/0002-verify-hard-gate.md is Proposed while AGENTS.md treats it as a hard constraint
- Summary: 1 fail(s), 7 warning(s)

实际 warning 数可随 ADR 状态和 CI 文件变化而变化；当前模板仓库预期退出码为 1，因为模板本身保留待用户替换的项目元信息。没有项目 manifest 时报告为 `WARN`，不计入失败。
```

- [ ] **步骤 4：提交 doctor 切片**

执行：

```bash
git status --short
git add scripts/scaffold-doctor.sh
git commit -m "feat(scaffold): add read-only scaffold doctor"
```

预期：

```text
仅暂存并提交 doctor 脚本。
```

### 任务 3：更新接入与维护文档

**文件：**

- 新建：无
- 修改：
  - `README.md`
  - `CONTRIBUTING.md`
- 测试：
  - `rg -n 'scaffold-doctor|adoption-checklist|接入自检' README.md CONTRIBUTING.md`

- [ ] **步骤 1：更新 README 接入步骤**

在 `README.md` 的 "接入后的 4 步" 中，把标题改为 "接入后的 5 步"，并在定义 `verify` 后增加自检步骤。最终该段应表达：

```markdown
## 接入后的 5 步

1. **补全项目元信息**——编辑 `AGENTS.md` 顶部的"用户项目元信息"，填入包管理器、命令、入口等
2. **必须定义 `verify` 命令**——在你项目的 manifest 中定义一个 `verify` 入口，串联 lint → typecheck → test → build；L1+ 任务完成前 AI 必跑（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）
3. **运行接入自检**——执行 `bash scripts/scaffold-doctor.sh`，并按 [adoption-checklist.md](docs/ai/checklists/adoption-checklist.md) 处理 `FAIL` / `WARN`；doctor 只检查脚手架接入状态，不替代项目 `verify`
4. **跑一次 L0 任务试水**——用本文档试一次小改动，跑一次最小验证
5. **跑一次 L2 任务验证流程**——按 [l2-multi-session-runbook.md](docs/ai/runbooks/l2-multi-session-runbook.md) + [feature-delivery-runbook.md](docs/ai/runbooks/feature-delivery-runbook.md) 跑通一次新功能（4 session 串行：设计 → 计划 → 实施 → 评审）
```

- [ ] **步骤 2：更新 README 模板与清单列表**

在 `README.md` 的 "模板与清单" 列表中增加：

```markdown
- 接入自检清单：[docs/ai/checklists/adoption-checklist.md](docs/ai/checklists/adoption-checklist.md)
```

- [ ] **步骤 3：更新 README 目录结构**

在 `README.md` 的目录结构中增加：

```text
├── scripts/
│   └── scaffold-doctor.sh          # 只读接入自检脚本
```

并在 `docs/ai/checklists/` 下增加：

```text
│       ├── adoption-checklist.md
│       └── review-checklist.md
```

- [ ] **步骤 4：更新 CONTRIBUTING 验证清单**

在 `CONTRIBUTING.md` 的 "验证清单（修改后自检）" 中增加：

```markdown
- [ ] 跑 `bash -n scripts/scaffold-doctor.sh`
- [ ] 跑 `bash scripts/scaffold-doctor.sh`，确认输出中的 `FAIL` / `WARN` 与当前模板状态一致
```

并在 "单点化原则" 或 "语言无关原则的边界" 附近补一句：

```markdown
`scripts/scaffold-doctor.sh` 只能做只读检查，不得自动修改用户项目文件或引入具体语言运行时依赖。
```

- [ ] **步骤 5：检查文档链接和关键词**

执行：

```bash
rg -n 'scaffold-doctor|adoption-checklist|接入自检' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md
```

预期：

```text
README、CONTRIBUTING、adoption checklist 均有命中。
```

- [ ] **步骤 6：提交文档接入切片**

执行：

```bash
git status --short
git add README.md CONTRIBUTING.md
git commit -m "docs(scaffold): document adoption self-check"
```

预期：

```text
仅暂存并提交 README 与 CONTRIBUTING 更新。
```

### 任务 4：最终验证与证据回写

**文件：**

- 新建：无
- 修改：
  - `docs/specs/2026-06-16-adoption-self-check.md`
  - `docs/plans/2026-06-16-adoption-self-check.md`
- 测试：
  - `bash -n scripts/scaffold-doctor.sh`
  - `bash scripts/scaffold-doctor.sh`
  - `rg -n '<[^>]+>' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md scripts/scaffold-doctor.sh`
  - `rg -n 'scaffold-doctor|adoption-checklist|接入自检' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md`
  - `git status --short`

- [ ] **步骤 1：运行 shell 语法检查**

执行：

```bash
bash -n scripts/scaffold-doctor.sh
```

预期：

```text
退出码 0，无语法错误。
```

- [ ] **步骤 2：运行 doctor**

执行：

```bash
bash scripts/scaffold-doctor.sh
```

预期：

```text
在模板仓库中，doctor 可以报告保留给用户替换的占位符和 ADR 状态 warning。若退出码为 1，必须确认失败项来自模板刻意保留的接入占位，而不是脚本错误。
```

- [ ] **步骤 3：运行占位符扫描**

执行：

```bash
rg -n '<[^>]+>' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md scripts/scaffold-doctor.sh
```

预期：

```text
所有命中均为示例占位符、检查目标字符串或脚本正则；不得出现未解释的新增必填占位。
```

- [ ] **步骤 4：运行接入关键词扫描**

执行：

```bash
rg -n 'scaffold-doctor|adoption-checklist|接入自检' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md
```

预期：

```text
README、CONTRIBUTING、adoption checklist 均能被检索到。
```

- [ ] **步骤 5：把验证证据写回 spec 和 plan**

在 `docs/specs/2026-06-16-adoption-self-check.md` 与本 plan 的 `## 验证证据` 段记录实际命令、退出码、关键输出和未跑项。doctor 如果因模板保留占位符而退出 1，应在备注中标注"预期失败，暴露接入占位"。

- [ ] **步骤 6：提交验证证据切片**

执行：

```bash
git status --short
git add docs/specs/2026-06-16-adoption-self-check.md docs/plans/2026-06-16-adoption-self-check.md
git commit -m "docs(plan): record adoption self-check verification"
```

预期：

```text
仅暂存并提交验证证据更新。
```

---

## 验证证据（实施 session 末尾必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `bash -n scripts/scaffold-doctor.sh` | 0 | `EXIT_CODE=0` | shell 语法检查通过 |
| `bash scripts/scaffold-doctor.sh` | 1 | `Summary: 1 fail(s), 7 warning(s)` | 预期失败；模板仓库保留 `AGENTS.md` 项目元信息占位符，并报告 manifest / CI / ADR 状态提示 |
| `rg -n '<[^>]+>' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md scripts/scaffold-doctor.sh` | 0 | 命中 README 示例占位符、CONTRIBUTING 提交信息示例、checklist 检查目标和脚本正则 | 未发现未解释的新增必填占位 |
| `rg -n 'scaffold-doctor|adoption-checklist|接入自检' README.md CONTRIBUTING.md docs/ai/checklists/adoption-checklist.md` | 0 | README、CONTRIBUTING、adoption checklist 均有命中 | 接入入口可检索 |
| `git status --short` | 0 | `M docs/plans/2026-06-16-adoption-self-check.md` | 写入验证证据前，除 plan 同步修正外无未提交实现文件 |

未跑项：项目根 `verify` 未运行；当前模板仓库无项目 manifest / verify 入口，doctor 已以 `WARN no common project manifest found` 暴露该接入缺口。本次按 plan 使用脚本语法、doctor、占位符扫描和关键词扫描作为替代验证。

## 批准（L3 任务必填，其他任务留空）

- 不适用，本任务按 `L2` 处理。
