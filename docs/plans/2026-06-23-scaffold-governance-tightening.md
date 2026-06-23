# Scaffold Governance Tightening 实施计划

> **基于 spec**：[docs/specs/2026-06-23-scaffold-governance-tightening.md](../specs/2026-06-23-scaffold-governance-tightening.md)
> （此行**必填**，否则视为与 spec 失联，详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)）

> **面向 Agent 执行者：** 本任务为 `L3`。实施前必须确认用户批准信号引用本 plan 或对应 spec 路径。无批准不得删除 `.claude/`，不得 patch 治理文件，不得 `git add` / `git commit` / push。

**目标：** 收紧脚手架治理结构，删除 Claude 专属配置，修正规则漂移，统一 ADR 状态，并让 doctor 区分模板状态与已接入状态。

**实现方式：** 按可验证切片修改文档和只读 shell 脚本；不引入依赖，不新增工具专属配置。

**技术栈：** Markdown + POSIX shell。

---

## 全局约束

- 任务级别：`L3`
- 默认工作区：隔离 worktree
- 不引入任何运行时依赖
- 不新增 Claude / Cursor / Aider / Copilot 等工具专属配置
- 保留 L3 无批准不得 `git add` / `git commit` / patch / push 的治理规则
- doctor 只能只读检查，不自动修改用户项目文件
- 若实施中需要超出文件清单的仓库级行为变化，停止并重新请求批准

## 文件清单

- 删除：
  - `.claude/settings.json`
  - `.claude/hooks/README.md`
- 修改：
  - `README.md`
  - `CONTRIBUTING.md`
  - `AGENTS.md`
  - `docs/CONTEXT.md`
  - `docs/ai/context-index.md`
  - `docs/ai/checklists/adoption-checklist.md`
  - `docs/adr/0002-verify-hard-gate.md`
  - `docs/adr/0003-multi-session-l2.md`
  - `docs/adr/0004-l2-spec-and-plan.md`
  - `docs/adr/0005-l3-approval-gate.md`
  - `docs/adr/README.md`
  - `scripts/scaffold-doctor.sh`
- 测试：
  - `bash -n scripts/scaffold-doctor.sh`
  - `bash scripts/scaffold-doctor.sh --template`
  - `bash scripts/scaffold-doctor.sh --adopted`
  - `rg -n '\.claude|Claude Code hooks|settings.json' README.md CONTRIBUTING.md AGENTS.md docs/ai docs/adr scripts`
  - `rg -n 'spec 或 plan|正式 spec 或 plan' docs/ai AGENTS.md README.md`
  - `rg -n '^Proposed' docs/adr/0002-verify-hard-gate.md docs/adr/0003-multi-session-l2.md docs/adr/0004-l2-spec-and-plan.md docs/adr/0005-l3-approval-gate.md`

## 非目标

- 不新增 `.scaffold-profile.yml` 或类似配置文件。
- 不把 CI 模板变成可直接运行的项目 CI。
- 不新增 PR 模板、CODEOWNERS 或 issue 流转。
- 不改变 L3 批准规则的内容，只去除 Claude 专属适配暗示。

### 任务 1：删除 Claude 专属层并修正文档引用

**文件：**

- 删除：`.claude/settings.json`、`.claude/hooks/README.md`
- 修改：`README.md`、`CONTRIBUTING.md`

**接口：**

- 消费：现有跨工具兼容定位
- 产出：工具无关的 L3 gate 描述，不再引用 Claude 专属配置目录

- [ ] **步骤 1：确认 `.claude` 引用位置**

执行：

```bash
rg -n '\.claude|Claude Code hooks|settings.json' README.md CONTRIBUTING.md AGENTS.md docs scripts .claude
```

预期：命中 README 的跨工具 / 目录树说明、`.claude` 自身文件。

- [ ] **步骤 2：删除 `.claude` 目录**

删除：

```text
.claude/settings.json
.claude/hooks/README.md
```

- [ ] **步骤 3：更新 README**

将 README 中 `.claude/`、Claude hooks 占位、目录树里的 `.claude` 段删除或改为工具无关说明。保留“核心约束通过 `AGENTS.md` 表达”的定位。

- [ ] **步骤 4：更新 CONTRIBUTING**

如存在工具专属配置维护暗示，改为“不要新增工具专属配置；如确需新增，按 L3 + ADR 处理”。

- [ ] **步骤 5：验证 Claude 引用收敛**

执行：

```bash
rg -n '\.claude|Claude Code hooks|settings.json' README.md CONTRIBUTING.md AGENTS.md docs/ai docs/adr scripts
```

预期：无命中；如有命中，必须是明确的历史说明并由实施者判断是否保留。

### 任务 2：修正 L2 spec+plan 表述漂移

**文件：**

- 修改：`docs/ai/context-index.md`、必要时 `AGENTS.md` / `README.md`

**接口：**

- 消费：ADR-0004 和 `task-levels.md` 的 L2 双份准入规则
- 产出：所有 L2 准入语境都使用 “spec 和 plan 双份” 或快速通道例外表述

- [ ] **步骤 1：扫描旧表述**

执行：

```bash
rg -n 'spec 或 plan|正式 spec 或 plan|spec / plan' AGENTS.md README.md docs/ai docs/adr
```

预期：找到需要区分的旧表述和中性表述。

- [ ] **步骤 2：修正准入语境**

把 L2 准入语境中的 “spec 或 plan” 改为 “spec 和 plan 双份”。保留合理的 “spec / plan” 中性路径描述。

- [ ] **步骤 3：验证旧表述消失**

执行：

```bash
rg -n 'spec 或 plan|正式 spec 或 plan' AGENTS.md README.md docs/ai docs/adr
```

预期：无 L2 准入语境命中。

### 任务 3：统一 ADR 状态语义

**文件：**

- 修改：`docs/adr/0002-verify-hard-gate.md`、`0003`、`0004`、`0005`、必要时 `docs/adr/README.md`

**接口：**

- 消费：`AGENTS.md` 已把 ADR-0002 至 ADR-0005 作为硬约束依据
- 产出：ADR 状态与硬约束使用方式一致

- [ ] **步骤 1：查看 ADR 状态**

执行：

```bash
rg -n '^## 状态|^Proposed|^Accepted' docs/adr/0002-verify-hard-gate.md docs/adr/0003-multi-session-l2.md docs/adr/0004-l2-spec-and-plan.md docs/adr/0005-l3-approval-gate.md
```

预期：当前 4 个 ADR 均为 `Proposed`。

- [ ] **步骤 2：改为 Accepted**

将 4 个 ADR 的状态从 `Proposed` 改为 `Accepted`。ADR-0004 保留 “Amends ADR-0001 L2 段” 语义，例如 `Accepted（Amends ADR-0001 L2 段）`。

- [ ] **步骤 3：验证 Proposed 不再命中**

执行：

```bash
rg -n '^Proposed' docs/adr/0002-verify-hard-gate.md docs/adr/0003-multi-session-l2.md docs/adr/0004-l2-spec-and-plan.md docs/adr/0005-l3-approval-gate.md
```

预期：无命中。

### 任务 4：引入最小 adoption profile 概念

**文件：**

- 修改：`AGENTS.md`、`docs/ai/context-index.md`、`docs/ai/checklists/adoption-checklist.md`

**接口：**

- 消费：现有 “用户项目元信息” 段
- 产出：明确命名的 adoption profile，仍以 `AGENTS.md` 表格作为填写位置

- [ ] **步骤 1：在 AGENTS.md 命名 adoption profile**

将 “用户项目元信息” 小节补充为 adoption profile 的单一填写入口。说明它包含包管理器、入口锚点、共享目录、测试目录和 verify 入口。

- [ ] **步骤 2：在 context-index 引用 adoption profile**

把 “主要代码锚点” 的示例占位说明改成读取 `AGENTS.md` adoption profile，不新增第二份元信息源。

- [ ] **步骤 3：在 adoption checklist 中使用同一术语**

让 checklist 检查项明确围绕 adoption profile 是否填写。

- [ ] **步骤 4：验证术语可检索**

执行：

```bash
rg -n 'adoption profile|项目元信息|用户项目元信息' AGENTS.md docs/ai/context-index.md docs/ai/checklists/adoption-checklist.md
```

预期：三处文件都能检索到该概念，且没有第二个配置源。

### 任务 5：调整 doctor 为 template / adopted 两种模式

**文件：**

- 修改：`scripts/scaffold-doctor.sh`、`README.md`、`docs/ai/checklists/adoption-checklist.md`

**接口：**

- 消费：adoption profile 概念
- 产出：`--template` 用于模板仓库自检，`--adopted` 用于目标项目接入检查

- [ ] **步骤 1：设计 doctor 模式行为**

目标行为：

```text
bash scripts/scaffold-doctor.sh --template
```

预期：模板仓库允许 `AGENTS.md` 保留必填占位符，允许 CI 模板保留 `<...>`，但仍检查 docs/specs、docs/plans、ADR 状态和脚本自身可读性。

```text
bash scripts/scaffold-doctor.sh --adopted
```

预期：目标项目中 `AGENTS.md` 必填占位符、CI `<...>`、缺 verify 入口仍按现有 FAIL / WARN 逻辑报告。

默认模式：

```text
bash scripts/scaffold-doctor.sh
```

预期：等价于 `--adopted`，保持接入用户的旧命令可用。

- [ ] **步骤 2：更新 shell 脚本**

为脚本增加参数解析：

```sh
mode=adopted
case "${1:-}" in
  ""|--adopted) mode=adopted ;;
  --template) mode=template ;;
  -h|--help) print usage and exit 0 ;;
  *) fail unsupported mode ;;
esac
```

在 `template` 模式下：

- `AGENTS.md` 占位符输出 `PASS` 或 `WARN`，不计为 `FAIL`
- CI `<...>` 输出 `PASS` 或 `WARN`，不计为 `FAIL`
- 无 manifest / verify 入口继续 `WARN`

- [ ] **步骤 3：更新 README 和 checklist**

README 接入步骤使用默认 `bash scripts/scaffold-doctor.sh`。模板维护说明使用 `bash scripts/scaffold-doctor.sh --template`。

- [ ] **步骤 4：验证两种模式**

执行：

```bash
bash -n scripts/scaffold-doctor.sh
bash scripts/scaffold-doctor.sh --template
bash scripts/scaffold-doctor.sh --adopted
```

预期：`--template` 不因模板占位符失败；`--adopted` 在当前模板仓库仍暴露接入未完成状态。

### 任务 6：最终文档自检与验证证据回写

**文件：**

- 修改：`docs/plans/2026-06-23-scaffold-governance-tightening.md`
- 可能修改：`docs/specs/2026-06-23-scaffold-governance-tightening.md`

**接口：**

- 消费：前 5 个切片结果
- 产出：验证证据

- [ ] **步骤 1：运行完整文档检查**

执行：

```bash
bash -n scripts/scaffold-doctor.sh
bash scripts/scaffold-doctor.sh --template
bash scripts/scaffold-doctor.sh --adopted
rg -n '\.claude|Claude Code hooks|settings.json' README.md CONTRIBUTING.md AGENTS.md docs/ai docs/adr scripts
rg -n 'spec 或 plan|正式 spec 或 plan' AGENTS.md README.md docs/ai
rg -n '^Proposed' docs/adr/0002-verify-hard-gate.md docs/adr/0003-multi-session-l2.md docs/adr/0004-l2-spec-and-plan.md docs/adr/0005-l3-approval-gate.md
git status --short
```

预期：检查结果与本 plan 的目标一致。

- [ ] **步骤 2：写入验证证据**

把实际命令、退出码、关键输出和未跑项写入本文件 `## 验证证据`。

---

## 批准（L3 任务必填）

- 批准时间：2026-06-23
- 批准来源：用户会话消息：“已批准实施 /Users/xuxz/repos/ruihui/.worktrees/ai-driven-scaffold/chore-scaffold-governance-tightening/docs/specs/2026-06-23-scaffold-governance-tightening.md 和 /Users/xuxz/repos/ruihui/.worktrees/ai-driven-scaffold/chore-scaffold-governance-tightening/docs/plans/2026-06-23-scaffold-governance-tightening.md”
- 批准范围：与 spec 显式声明的范围一致

## 验证证据（实施 session 末尾必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `bash -n scripts/scaffold-doctor.sh` | 0 | 无输出 | shell 语法检查通过 |
| `bash scripts/scaffold-doctor.sh --template` | 0 | `Summary: 0 fail(s), 4 warning(s)` | 模板仓库允许 Adoption Profile / CI 占位符；warnings 为预期模板状态 |
| `bash scripts/scaffold-doctor.sh --adopted` | 1 | `Summary: 1 fail(s), 3 warning(s)` | 当前仓库仍是模板状态；已接入项目模式按预期暴露未填写 Adoption Profile |
| `rg -n '\.claude\|Claude Code hooks\|settings.json' README.md CONTRIBUTING.md AGENTS.md docs/ai docs/adr scripts` | 1 | 无命中 | 负向检查通过：面向治理入口和 ADR 的 Claude 专属引用已清除 |
| `rg -n 'spec 或 plan\|正式 spec 或 plan' AGENTS.md README.md docs/ai` | 1 | 无命中 | 负向检查通过：现行入口不再保留 L2 “spec 或 plan”旧表述 |
| `rg -n '^Proposed' docs/adr/0002-verify-hard-gate.md docs/adr/0003-multi-session-l2.md docs/adr/0004-l2-spec-and-plan.md docs/adr/0005-l3-approval-gate.md` | 1 | 无命中 | 负向检查通过：ADR-0002 至 ADR-0005 不再是 `Proposed` |
| `git status --short` | 0 | 列出 `.claude` 删除、治理文档修改、spec/plan 新增 | 工作区仍有本任务预期改动，尚未提交 |

未跑项：项目根 `verify` 未运行；当前模板仓库无项目 manifest / verify 入口，doctor 已以 `WARN no common project manifest found` 暴露该模板状态。本文档调整按 plan 使用 shell 语法检查、doctor 双模式和文档负向扫描作为替代验证。
