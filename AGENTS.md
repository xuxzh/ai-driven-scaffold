# AGENTS.md

本仓库采用"**文档驱动、验证优先、AI 受控执行**"的开发方式。

本文件是仓库级统一入口，被以下 AI 工具自动读取：

- Claude Code（`AGENTS.md` 优先于 `CLAUDE.md`）
- Cursor（`.cursorrules` / `AGENTS.md` 兼容）
- Aider（`CONVENTIONS.md` / `AGENTS.md` 兼容）
- GitHub Copilot（仓库级指令）
- 其他支持项目级指令的工具

> 任何 AI 工具在进入本仓库后，**必须**先读本文件，再按文件中的链接读取治理单点定义。
>
> 本文件只保留矩阵短摘要与权威链接，**条件不再此处重新定义**；所有等级 / 分支 / worktree / session 的具体规则以 [docs/ai/task-levels.md](docs/ai/task-levels.md) 与 [docs/ai/branch-strategy.md](docs/ai/branch-strategy.md) 为准。

## 治理入口

按以下顺序阅读，建立对仓库的最小必要理解：

- 上下文导航：[docs/ai/context-index.md](docs/ai/context-index.md)
- 治理基线：[docs/ai/governance-core.md](docs/ai/governance-core.md)
- 任务分级 L0/L1/L2/L3：[docs/ai/task-levels.md](docs/ai/task-levels.md)
- 完成定义：[docs/ai/completion-criteria.md](docs/ai/completion-criteria.md)
- 验证基线：[docs/ai/verification-baseline.md](docs/ai/verification-baseline.md)
- 分支与 worktree：[docs/ai/branch-strategy.md](docs/ai/branch-strategy.md)
- AI 角色边界：[docs/ai/ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)
- 文档回写规则：[docs/ai/doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md)
- 术语表：[docs/CONTEXT.md](docs/CONTEXT.md)
- 长期决策：[docs/adr/](docs/adr/)（其中 ADR-0002 / 0003 / 0004 / 0005 是本治理基线的硬约束依据）

## AI 工作规则（执行前必读）

1. **任何代码改动前，先说明变更级别**：`L0` / `L1` / `L2` / `L3`（详见 [task-levels.md](docs/ai/task-levels.md)）
2. **实质性编辑前先检查当前分支**：不得在 `main` / `master` 直接提交开发改动；`L1+` 强制独立 worktree（详见 [branch-strategy.md](docs/ai/branch-strategy.md)）
3. **默认使用任务分支** `<prefix>-<task-slug>`（前缀按改动类型：`feat-` / `fix-` / `refactor-` / `chore-` / `docs-` / `test-` / `perf-` / `build-` / `ci-`，详见 [branch-strategy.md](docs/ai/branch-strategy.md)）
4. **`L2` 默认 spec 和 plan 双份都需提交**（详见 [task-levels.md](docs/ai/task-levels.md) 与 [ADR-0004](docs/adr/0004-l2-spec-and-plan.md)）
5. **多 session 串行 / session 数**：以 [ADR-0003](docs/adr/0003-multi-session-l2.md) 与对应 runbook 为权威，本文件不再复述
6. **`L3` 实施 session 启动前必须收用户明确批准信号**（详见 [ADR-0005](docs/adr/0005-l3-approval-gate.md)）
7. **L1+ 任务完成前必须运行 `verify` 并写入汇报**（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）
8. **完成后必须给出验证证据**：实际跑了哪些命令、哪些通过、哪些未跑及原因
9. **触及长期约定时按回写规则更新文档**（[doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md)）
10. **不得自行扩大任务范围**（详见 [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)）

## 任务入口速查（短摘要；条件见权威文件）

| 任务类型 | 等级 / 条件 | 入口与权威链接 |
|---|---|---|
| `L0` 单文件、不跨模块、不改变默认行为 | 至少运行最小验证 | 条件：[task-levels.md](docs/ai/task-levels.md)；分支：[branch-strategy.md](docs/ai/branch-strategy.md) |
| `L1` 单目标常规改动 | task packet 先行；任务分支 + 独立 worktree | 模板：[task-packet.md](docs/ai/templates/task-packet.md)；条件：[task-levels.md](docs/ai/task-levels.md) |
| `L2` 跨文件行为、数据流、入口变化 | spec + plan 双文件；任务分支 + 独立 worktree | 模板：[feature-spec.md](docs/ai/templates/feature-spec.md) / [implementation-plan.md](docs/ai/templates/implementation-plan.md)；条件：[task-levels.md](docs/ai/task-levels.md)；编排：[ADR-0003](docs/adr/0003-multi-session-l2.md) |
| 业务功能 + API/UI 原型 | 通用编排 + feature-specific | [l2-multi-session-runbook.md](docs/ai/runbooks/l2-multi-session-runbook.md) + [feature-delivery-runbook.md](docs/ai/runbooks/feature-delivery-runbook.md) |
| 缺陷修复 | bugfix brief 先行；走通用编排 + bugfix-specific | [bugfix-brief.md](docs/ai/templates/bugfix-brief.md) / [bugfix-delivery-runbook.md](docs/ai/runbooks/bugfix-delivery-runbook.md) |
| 重构 | refactor brief 先行；走通用编排 + refactor-specific | [refactor-brief.md](docs/ai/templates/refactor-brief.md) / [refactor-delivery-runbook.md](docs/ai/runbooks/refactor-delivery-runbook.md) |
| 评审 | review checklist（建议开新 session） | [review-checklist.md](docs/ai/checklists/review-checklist.md) |
| `L3` CI、依赖、安全、鉴权、仓库级约定 | 人工主导 + L2 条件 + 实施前明确批准 | 条件：[task-levels.md](docs/ai/task-levels.md)；批准门禁：[ADR-0005](docs/adr/0005-l3-approval-gate.md) |

> **不重复定义**：本表的等级条件、分支、worktree、session 数等均以"条件 / 编排"链接所指的文件为权威；本文件不再复述 L0 on-main 例外、推荐 worktree、4 session 串行等任何过时表述——如有冲突，以权威链接为准。

## 用户项目元信息（本仓库的项目画像）

> 本仓库是脚手架自身，采用本治理时按以下事实推进；非"默认推荐"——任何项目在按 [template/AGENTS.md](template/AGENTS.md) 接入时必须按自身情况重填。

| 字段 | 本仓库值 |
|---|---|
| 包管理器 | pnpm（本仓库事实，非脚手架默认推荐） |
| 主要应用目录 | `docs/` |
| 入口代码锚点 | 无（纯文档仓库） |
| 共享包目录 | 无 |
| 测试目录 | 无 |
| 完整验证入口 | `bash scripts/scaffold-doctor.sh --template`（L0 可选、L1+ 必跑；本仓库无 manifest verify，详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)） |
| Isolation Profile | 默认策略（L0 可选 worktree；L1+ 强制独立 worktree）。如需 Strict Isolation Profile（所有等级强制 worktree），按 [branch-strategy.md](docs/ai/branch-strategy.md) 启用 |

> 采用本脚手架的新项目请复制 [template/AGENTS.md](template/AGENTS.md) → 根 `AGENTS.md`，按自身情况重填 7 个字段（含 Isolation Profile）。

## 重要边界（不要破坏）

- **不得在主分支直接提交开发改动**——见 [branch-strategy.md](docs/ai/branch-strategy.md)
- **不得自行扩大任务范围**——见 [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)
- **不得在没有验证证据时宣称完成**——见 [completion-criteria.md](docs/ai/completion-criteria.md)
- **不得把聊天结论当作长期知识资产**——按 [doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md) 回写

## 文档分层速记

| 关注点 | 位置 |
|---|---|
| 仓库级高频规则、AI 会话入口 | `AGENTS.md`（本文件） |
| 仓库术语表 | `docs/CONTEXT.md`（如适用） |
| AI 治理与工作流 | `docs/ai/` |
| 单次任务设计 | `docs/specs/` |
| 实施计划 | `docs/plans/` |
| 长期决策 | `docs/adr/` |
| 项目特定规范 | `docs/standards/`（如适用） |
| API/契约 | `docs/api/`（如适用） |