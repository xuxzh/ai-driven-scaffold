# 分支与 worktree 策略 · 快速摘要

> 本文仅为快速摘要；如有冲突，以链接的权威规范和 Accepted ADR 为准。

## 四个概念

| 概念 | 含义 | 谁创建 |
|---|---|---|
| 工作区落盘 | 当前 checkout 物理目录里的文件修改 | AI / 开发者 |
| 分支 | `git` 引用（`refs/heads/<name>`），决定 `HEAD` 指向 | 开发者 |
| 提交 | 在某条分支上的一次快照 | 开发者 |
| worktree | 同一仓库的额外物理工作区副本（`.worktrees/<branch>/`） | 开发者 |

## 主分支保护

- `main` / `master` **只作为稳定集成分支**，不直接承载开发提交
- 实质性编辑前必须先 `git branch --show-current` 与 `git status --short`
- 当前在主分支 → 立刻切任务分支（L0）或创建独立 worktree（L1+）
- 主分支上**不得**存在任何 L1+ 改动；L0 也必须先走任务分支

## 默认策略（任务分支 + worktree）

| 等级 | 任务分支 | 独立 worktree |
|---|---|---|
| `L0` | 必须 | 可选 |
| `L1` | 必须 | 必须 |
| `L2` | 必须 | 必须 |
| `L3` | 必须 | 必须 |

> L1+ 任何阶段（包括 L2 的 spec / plan 阶段）都必须在独立 worktree 上工作。

## Strict Isolation Profile

接入项目可在 `AGENTS.md` 的 Adoption Profile 中显式声明（`Isolation: strict`）；启用后：

- **所有等级**（含 L0）一律要求独立 worktree；**不**保留 L0 例外
- L0 仍只需最小验证，但必须在 worktree 中完成
- `main` / `master` 不允许任何直接落盘（含 L0）
- 撤回只能通过 ADR / 仓库级变更；不得在单次任务中临时关闭

未声明则视为默认策略（L0 可选 worktree）。

## 分支命名

格式：`<prefix>-<task-slug>`，`<prefix>` 按改动类型而非 AI 工具：

`feat-` / `fix-` / `refactor-` / `chore-` / `docs-` / `test-` / `perf-` / `build-` / `ci-`

- `<task-slug>` 用小写字母、数字、短横线，3–6 个单词
- 不使用 AI 工具代号作为前缀（`codex-` / `claude-` / `cursor-` 等）

## worktree 路径

默认放仓库根 `.worktrees/<branch-name>/`；只在磁盘 / 权限 / 调试需要时挪到其他位置，并写明原因。

## 会话起点（每个新 session 必做）

1. `git branch --show-current` 确认在哪个任务分支 / worktree
2. 从仓库文档读取上一 session 交付物（spec / plan / 验证证据 / Handoff）
3. **不**依赖会话历史推断上一 session 意图
4. 评审 session **建议**新开

## 汇报必须说明

- 实际用任务分支还是 worktree（两者并不等价）
- 是否声明 Strict Isolation Profile
- L2+ 当前是哪个 session
- 跑了哪些验证 / 哪些未跑及原因
- L3 的"已批准"信号来源（issue / 评论 / 显式消息）

## 权威来源

- 分支与 worktree：[branch-strategy.md](./branch-strategy.md)
- 任务分级：[task-levels.md](./task-levels.md)
- 接入模板：[../../template/AGENTS.md](../../template/AGENTS.md)
- ADR：[../adr/0003-multi-session-l2.md](../adr/0003-multi-session-l2.md) / [../adr/0005-l3-approval-gate.md](../adr/0005-l3-approval-gate.md)
