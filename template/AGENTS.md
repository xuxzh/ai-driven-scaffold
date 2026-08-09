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

## 分流入口

进入本仓库后，先回答"这次改动是什么级别"（用 [task-levels.md](docs/ai/task-levels.md) 的判定三问确定 `L0` / `L1` / `L2` / `L3`），再按下表取本次必读集；触发型文件在发生对应行为时再读：

| 改动级别 | 本次必读集 | 触发型（发生才读）|
|---|---|---|
| `L0` 单文件、不跨模块、不改变默认行为 | 本文件 + [context-index.md](docs/ai/context-index.md) + [task-levels.md](docs/ai/task-levels.md) + 代码锚点 | [commit-convention.md](docs/ai/commit-convention.md)（要提交时）|
| `L1` 单目标常规改动 | `L0` + [task-packet.md](docs/ai/templates/task-packet.md) + [branch-strategy.md](docs/ai/branch-strategy.md) + [verification-baseline.md](docs/ai/verification-baseline.md) | [doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md)（触及长期约定时）|
| `L2` 跨文件行为、数据流、入口变化 | `L1` + 对应 runbook + [feature-spec.md](docs/ai/templates/feature-spec.md) / [implementation-plan.md](docs/ai/templates/implementation-plan.md) + [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md) + [completion-criteria.md](docs/ai/completion-criteria.md) | [ADR-0003](docs/adr/0003-multi-session-l2.md) / [ADR-0004](docs/adr/0004-l2-spec-and-plan.md)（有争议时）|
| `L3` CI、依赖、安全、鉴权、仓库级约定 | `L2` + [ADR-0005](docs/adr/0005-l3-approval-gate.md) + 对应 brief | [ADR-0001](docs/adr/0001-task-level-governance.md) / [ADR-0002](docs/adr/0002-verify-hard-gate.md)（有争议时）|

> 本表是入口唯一权威；导航 / 规则 / 依据 / 模板四层的具体内容由各自单点文件承载，本文件不复述。深路径（`L2+` 多 session 角色分流）见 [context-index.md](docs/ai/context-index.md)。

## 用户项目元信息（Adoption Profile，clone 后必须补充）

> 本段是目标项目的 **Adoption Profile**，由项目维护者补充。AI 工具在执行任何命令前必须读取本段，否则无法正确定位锚点和验证入口。

**填写方式**：
- 把下面各行的占位符替换为本项目的实际值
- 替换完成后，**删除本段下方的"参考示例"代码块**（避免示例值与填写值混淆）
- 如不适用某项，填"无"
- `Isolation Profile` 字段决定工作区与 worktree 强制粒度，详见 [branch-strategy.md](docs/ai/branch-strategy.md)

| 字段 | 占位符 | 你的项目值 |
|---|---|---|
| 包管理器 | `<pm>` | （填 pnpm / npm / yarn / uv / cargo / go / mix 等） |
| 主要应用目录 | `<app-dir>` | （填 src/、apps/web/、internal/、cmd/ 等） |
| 入口代码锚点 | `<entry-file>` | （填主入口文件路径） |
| 共享包目录 | `<shared-dir>` | （如不适用填"无"） |
| 测试目录 | `<test-dir>` | （填 tests/、__tests__/、*_test.go 等） |
| 最小验证入口 | `<command>` | （必填；L0 任务的最小验证命令；不适用需写"不适用 + 理由"） |
| L1 验证入口 | `<command>` | （可选；L1 任务的受影响层验证命令；不适用填"无"） |
| 快速验证入口 | `<command>` | （可选；L2 无主链路 / 构建风险时的快速验证命令；不适用填"无"） |
| 完整验证入口 | `<command>` | （**必须**；L2 触及主链路 / 数据流 / 入口 / 构建 + L3 必填；`full` 必填，必须显式串联 lint → typecheck → test → build；L1+ 任务完成前 AI 必跑，详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)） |
| Isolation Profile | `default` 或 `strict` | （`default`：L0 可选 worktree，L1+ 强制；`strict`：所有等级强制 worktree，详见 [branch-strategy.md](docs/ai/branch-strategy.md)） |

填写完成后，AGENTS.md 中应**不再出现** `<...>` 占位符。

> **档位语义**：4 个验证入口字段对应 [verification-baseline.md](docs/ai/verification-baseline.md) 的 `minimal / l1 / fast / full` 4 档。`minimal` 与 `full` 必填；`l1` 与 `fast` 不适用时填"无"并写明理由。未跑任一档位时必须在 verify 报告 / `## 验证证据` 段显式标注（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）。

## 重要边界（不要破坏）

- **不得在主分支直接提交开发改动**——见 [branch-strategy.md](docs/ai/branch-strategy.md)
- **AI 默认不得自动 commit / 不得跳过 hooks / 不得 amend 未授权提交**——见 [commit-convention.md](docs/ai/commit-convention.md)
- **不得自行扩大任务范围**——见 [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)
- **不得在没有验证证据时宣称完成**——见 [completion-criteria.md](docs/ai/completion-criteria.md)
- **不得把聊天结论当作长期知识资产**——按 [doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md) 回写

