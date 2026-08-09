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
> 本文件只保留矩阵短摘要与权威链接，**条件不再此处重新定义**；所有等级 / 分支 / worktree / session 的具体规则以 [template/docs/ai/task-levels.md](template/docs/ai/task-levels.md) 与 [template/docs/ai/branch-strategy.md](template/docs/ai/branch-strategy.md) 为准。

## AI 工作规则（执行前必读）

1. **任何代码改动前，先说明变更级别**：`L0` / `L1` / `L2` / `L3`（详见 [task-levels.md](template/docs/ai/task-levels.md)）
2. **实质性编辑前先检查当前分支**：不得在 `main` / `master` 直接提交开发改动；`L1+` 强制独立 worktree（详见 [branch-strategy.md](template/docs/ai/branch-strategy.md)）
3. **默认使用任务分支** `<prefix>-<task-slug>`（前缀按改动类型：`feat-` / `fix-` / `refactor-` / `chore-` / `docs-` / `test-` / `perf-` / `build-` / `ci-`，详见 [branch-strategy.md](template/docs/ai/branch-strategy.md)）
4. **`L2` 默认 spec 和 plan 双份都需提交**（详见 [task-levels.md](template/docs/ai/task-levels.md) 与 [ADR-0004](template/docs/adr/0004-l2-spec-and-plan.md)）
5. **多 session 串行 / session 数**：以 [ADR-0003](template/docs/adr/0003-multi-session-l2.md) 与对应 runbook 为权威，本文件不再复述
6. **`L3` 实施 session 启动前必须收用户明确批准信号**（详见 [ADR-0005](template/docs/adr/0005-l3-approval-gate.md)）
7. **L1+ 任务完成前必须运行 `verify` 并写入汇报**（详见 [ADR-0002](template/docs/adr/0002-verify-hard-gate.md)）
8. **完成后必须给出验证证据**：实际跑了哪些命令、哪些通过、哪些未跑及原因
9. **触及长期约定时按回写规则更新文档**（[doc-rewriting-rules.md](template/docs/ai/doc-rewriting-rules.md)）
10. **不得自行扩大任务范围**（详见 [ai-role-boundaries.md](template/docs/ai/ai-role-boundaries.md)）

## 分流入口

进入本仓库后，先回答"这次改动是什么级别"（用 [task-levels.md](template/docs/ai/task-levels.md) 的判定三问确定 `L0` / `L1` / `L2` / `L3`），再按下表取本次必读集；触发型文件在发生对应行为时再读：

| 改动级别 | 本次必读集 | 触发型（发生才读）|
|---|---|---|
| `L0` 单文件、不跨模块、不改变默认行为 | 本文件 + [context-index.md](template/docs/ai/context-index.md) + [task-levels.md](template/docs/ai/task-levels.md) + 代码锚点 | [commit-convention.md](template/docs/ai/commit-convention.md)（要提交时）|
| `L1` 单目标常规改动 | `L0` + [task-packet.md](template/docs/ai/templates/task-packet.md) + [branch-strategy.md](template/docs/ai/branch-strategy.md) + [verification-baseline.md](template/docs/ai/verification-baseline.md) | [doc-rewriting-rules.md](template/docs/ai/doc-rewriting-rules.md)（触及长期约定时）|
| `L2` 跨文件行为、数据流、入口变化 | `L1` + 对应 runbook + [feature-spec.md](template/docs/ai/templates/feature-spec.md) / [implementation-plan.md](template/docs/ai/templates/implementation-plan.md) + [ai-role-boundaries.md](template/docs/ai/ai-role-boundaries.md) + [completion-criteria.md](template/docs/ai/completion-criteria.md) | [ADR-0003](template/docs/adr/0003-multi-session-l2.md) / [ADR-0004](template/docs/adr/0004-l2-spec-and-plan.md)（有争议时）|
| `L3` CI、依赖、安全、鉴权、仓库级约定 | `L2` + [ADR-0005](template/docs/adr/0005-l3-approval-gate.md) + 对应 brief | [ADR-0001](template/docs/adr/0001-task-level-governance.md) / [ADR-0002](template/docs/adr/0002-verify-hard-gate.md)（有争议时）|

> 本表是入口唯一权威；导航 / 规则 / 依据 / 模板四层的具体内容由各自单点文件承载，本文件不复述。深路径（`L2+` 多 session 角色分流）见 [context-index.md](template/docs/ai/context-index.md)。

## 用户项目元信息（本仓库的项目画像）

> 本仓库是脚手架自身，采用本治理时按以下事实推进；非"默认推荐"——任何项目在按 [template/AGENTS.md](template/AGENTS.md) 接入时必须按自身情况重填。

| 字段 | 本仓库值 |
|---|---|
| 包管理器 | pnpm（本仓库事实，非脚手架默认推荐） |
| 主要应用目录 | `docs/` |
| 入口代码锚点 | 无（纯文档仓库） |
| 共享包目录 | 无 |
| 测试目录 | 无 |
| 最小验证入口 | `bash template/scripts/scaffold-doctor.sh --template`（必填；纯文档仓库的最小验证即 doctor 本体） |
| L1 验证入口 | 无（不适用，理由：纯文档仓库无独立 L1 层验证，与 minimal 等价） |
| 快速验证入口 | 无（不适用，理由：纯文档仓库无主链路 / 构建风险分层） |
| 完整验证入口 | `bash template/scripts/scaffold-doctor.sh --template`（必填；本仓库无 manifest verify，详见 [ADR-0002](template/docs/adr/0002-verify-hard-gate.md)） |
| Isolation Profile | 默认策略（L0 可选 worktree；L1+ 强制独立 worktree）。如需 Strict Isolation Profile（所有等级强制 worktree），按 [branch-strategy.md](template/docs/ai/branch-strategy.md) 启用 |

> **档位语义**：4 个验证入口字段对应 [verification-baseline.md](template/docs/ai/verification-baseline.md) 的 `minimal / l1 / fast / full` 4 档。`minimal` 与 `full` 必填；`l1` 与 `fast` 不适用时填"无"并写明理由。未跑任一档位时必须在 verify 报告 / `## 验证证据` 段显式标注（详见 [ADR-0002](template/docs/adr/0002-verify-hard-gate.md)）。

> 采用本脚手架的新项目请复制 [template/AGENTS.md](template/AGENTS.md) → 根 `AGENTS.md`，按自身情况重填 10 个 Adoption Profile 字段（含 4 个验证入口、Isolation Profile、入口主文件、测试目录等）。

## 重要边界（不要破坏）

- **不得在主分支直接提交开发改动**——见 [branch-strategy.md](template/docs/ai/branch-strategy.md)
- **AI 默认不得自动 commit / 不得跳过 hooks / 不得 amend 未授权提交**——见 [commit-convention.md](template/docs/ai/commit-convention.md)
- **不得自行扩大任务范围**——见 [ai-role-boundaries.md](template/docs/ai/ai-role-boundaries.md)
- **不得在没有验证证据时宣称完成**——见 [completion-criteria.md](template/docs/ai/completion-criteria.md)
- **不得把聊天结论当作长期知识资产**——按 [doc-rewriting-rules.md](template/docs/ai/doc-rewriting-rules.md) 回写

