# AGENTS.md

本仓库采用"**文档驱动、验证优先、AI 受控执行**"的开发方式。

本文件是仓库级统一入口，被以下 AI 工具自动读取：

- Claude Code（`AGENTS.md` 优先于 `CLAUDE.md`）
- Cursor（`.cursorrules` / `AGENTS.md` 兼容）
- Aider（`CONVENTIONS.md` / `AGENTS.md` 兼容）
- GitHub Copilot（仓库级指令）
- 其他支持项目级指令的工具

> 任何 AI 工具在进入本仓库后，**必须**先读本文件，再按文件中的链接读取治理单点定义。

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

## AI 工作规则（执行前必读）

1. **任何代码改动前，先说明变更级别**：`L0` / `L1` / `L2` / `L3`（详见 [task-levels.md](docs/ai/task-levels.md)）
2. **实质性编辑前先检查当前分支**：不得在 `main` / `master` 直接提交开发改动（详见 [branch-strategy.md](docs/ai/branch-strategy.md)）
3. **默认使用任务分支** `codex-<task-slug>`；`L2`/`L3` 推荐使用 `.worktrees/` 下的 worktree
4. **`L2` 及以上必须先有正式 spec 或 plan**：`docs/specs/` 或 `docs/plans/`
5. **完成后必须给出验证证据**：实际跑了哪些命令、哪些通过、哪些未跑及原因
6. **触及长期约定时按回写规则更新文档**（[doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md)）
7. **不得自行扩大任务范围**（详见 [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)）

## 任务入口速查

| 任务类型 | 入口 | 模板 |
|---|---|---|
| `L0` 文案、注释、局部测试修复 | 直接做 + 最小验证 | — |
| `L1` 单目标常规改动 | task packet 先行 | [task-packet.md](docs/ai/templates/task-packet.md) |
| `L2` 新功能、跨文件行为 | spec 或 plan 先行 | [feature-spec.md](docs/ai/templates/feature-spec.md) / [implementation-plan.md](docs/ai/templates/implementation-plan.md) |
| 业务功能 + API/UI 原型 | 8 步交付 runbook | [feature-delivery-runbook.md](docs/ai/runbooks/feature-delivery-runbook.md) |
| 缺陷修复 | bugfix brief 先行 | [bugfix-brief.md](docs/ai/templates/bugfix-brief.md) |
| 评审 | review checklist | [review-checklist.md](docs/ai/checklists/review-checklist.md) |
| `L3` CI、依赖、安全、跨 workspace | 人工主导 + spec/plan | — |

## 用户项目元信息（clone 后必须补充）

> 以下信息由本项目维护者补充。AI 工具在执行任何命令前必须读取本段，否则无法正确执行验证。

- **包管理器**：`<pm>`（例如 pnpm / npm / yarn / uv / cargo / go / mix）
- **静态检查命令**：`<pm> lint`（如不适用填"无"）
- **类型检查命令**：`<pm> typecheck`（如不适用填"无"）
- **单元测试命令**：`<pm> test`
- **端到端测试命令**：`<pm> test:e2e`（如不适用填"无"）
- **构建命令**：`<pm> build`
- **完整验证入口**：建议在根 `package.json` / `Makefile` / `Cargo.toml` 等定义 `verify` 串联上述步骤
- **主要应用目录**：`<app-dir>`（例如 `src/`、`apps/web/`、`internal/`、`cmd/`）
- **入口代码锚点**：`<entry-file>`（例如 `src/main.ts`、`cmd/server/main.go`）
- **共享包目录**：`<shared-dir>`（如适用；否则填"无"）
- **测试目录**：`<test-dir>`（例如 `tests/`、`__tests__/`、`*_test.go`）

**示例填法**（仅供参考，可按项目实际栈选择其一）：

```markdown
# JavaScript / TypeScript 项目
- 包管理器：pnpm
- 静态检查命令：pnpm lint
- 类型检查命令：pnpm typecheck
- 单元测试命令：pnpm test
- 端到端测试命令：pnpm test:e2e
- 构建命令：pnpm build
- 完整验证入口：pnpm verify
- 主要应用目录：apps/web
- 入口代码锚点：apps/web/src/main.tsx

# Python 项目
- 包管理器：uv
- 静态检查命令：uv run ruff check .
- 类型检查命令：uv run mypy .
- 单元测试命令：uv run pytest
- 端到端测试命令：uv run pytest tests/e2e
- 构建命令：uv build
- 完整验证入口：make verify
- 主要应用目录：src/
- 入口代码锚点：src/main.py

# Go 项目
- 包管理器：go
- 静态检查命令：go vet ./...
- 类型检查命令：（无；Go 编译时已含类型检查）
- 单元测试命令：go test ./...
- 端到端测试命令：go test ./e2e/...
- 构建命令：go build ./...
- 完整验证入口：make verify
- 主要应用目录：cmd/ internal/
- 入口代码锚点：cmd/server/main.go
```

## 重要边界（不要破坏）

- **不得在主分支直接提交开发改动**——见 [branch-strategy.md](docs/ai/branch-strategy.md)
- **不得自行扩大任务范围**——见 [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)
- **不得在没有验证证据时宣称完成**——见 [completion-criteria.md](docs/ai/completion-criteria.md)
- **不得把聊天结论当作长期知识资产**——按 [doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md) 回写

## 文档分层速记

| 关注点 | 位置 |
|---|---|
| 仓库级高频规则、AI 会话入口 | `AGENTS.md`（本文件） |
| AI 治理与工作流 | `docs/ai/` |
| 单次任务设计 | `docs/specs/` |
| 实施计划 | `docs/plans/` |
| 长期决策 | `docs/adr/` |
| 项目特定规范 | `docs/standards/`（如适用） |
| API/契约 | `docs/api/`（如适用） |
