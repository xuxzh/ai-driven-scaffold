# AI 上下文索引 · 快速摘要

> 本文仅为快速摘要；如有冲突，以链接的权威规范和 Accepted ADR 为准。

## 3 分钟短路径（L0 / L1 单 session）

按顺序读：

1. `AGENTS.md`（仓库级高频边界）
2. [task-levels-summary.md](./task-levels-summary.md)（任务分级）
3. [branch-strategy-summary.md](./branch-strategy-summary.md)（分支 / worktree）
4. [docs/CONTEXT.md](../CONTEXT.md)（术语表）
5. 任务模板 / 代码锚点（按"按任务类型"选）

适用范围：`L0`、低风险 `L1`、评审前快速定位、熟悉仓库的新会话。

## 深路径（L2 / L3 多 session）

新会话**必须**先读 [session-handoff-protocol.md](./runbooks/session-handoff-protocol.md) 再读 Handoff：

- L2 规划 / 实施 Session → `docs/plans/<date>-<name>.md` 末尾 `## Session Handoff`
- L3 设计 Session（仅 spec） → `docs/specs/<date>-<name>.md` 的 `## Session Handoff`

仅凭 Handoff 的阶段 / 产物 / 验证 / 允许动作恢复状态；任一协议门禁失败时停止，不读取聊天历史补足。

## 按 Session 分流

| Session | 必读 | 必做 |
|---|---|---|
| L2 规划 | AGENTS.md + 任务分级摘要 + spec/plan 模板 + [ADR-0004](../adr/0004-l2-spec-and-plan.md) | 先写 spec → 用户确认 → 再写 plan |
| L2 实施 | AGENTS.md + 上一 session 交付物（spec + plan）+ 分支摘要 + [ADR-0002](../adr/0002-verify-hard-gate.md) | 跑 `verify` 并写入 `## 验证证据` |
| L2 评审（新开） | AGENTS.md + `git diff` + spec/plan + `## 验证证据` + [review-checklist.md](./checklists/review-checklist.md) + [ADR-0003](../adr/0003-multi-session-l2.md) | review report 必含测试盲区 + 未跑项 + spec/plan 物理分离判定 |
| L3 设计 | 同 L2 规划（只写到 spec） | 提交 spec 后转计划 session |
| L3 计划 | AGENTS.md + 上一 session spec + plan 模板 + verification-baseline | 提交 plan 后等"已批准" |
| L3 实施 | L2 实施 + [ADR-0005](../adr/0005-l3-approval-gate.md) | 缺批准信号时不得 `git add` / commit / patch / push |
| L3 评审 | L2 评审 + 核对 `## 批准` 段（批准信号 + 范围 + 引用 spec/plan 路径） | 按 L2 评审纪律 + L3 批准核对 |

## Session Handoff 恢复路径（11 必填字段）

任一缺失或 `Status: blocked` → 停止：

Task Level / Current Phase / Status / Completed / Artifacts（路径必须存在）/ Decisions / Assumptions / Open Questions / Verification（命令 + 退出码 + 关键输出 + 未跑项）/ Next Allowed Actions / Prohibited Scope。

物理落点：L2 规划 / 实施结束 → 对应 plan 末尾 `## Session Handoff`；评审结束 → plan review 段或独立 review report（必须回链 plan）。

## 按任务类型分流

| 任务类型 | 入口 | 必跑 |
|---|---|---|
| L0 | AGENTS.md + 快速摘要 + 锚点 | 最小验证 |
| L1 | [task-packet.md 模板](./templates/task-packet.md) + 规范 + 锚点 | L1 验证 |
| L2 | spec + plan 模板 + L2 三 Session | full 验证 |
| L2+ 批量 | [batch-ai-execution-runbook.md](./runbooks/batch-ai-execution-runbook.md) | 4 条件 + 8 字段 + Integration Verify |
| L3 | L2 + [ADR-0005](../adr/0005-l3-approval-gate.md) | 完整基线 + 人工确认 |

## 权威来源

- 上下文导航：[context-index.md](./context-index.md)
- Handoff 协议：[session-handoff-protocol.md](./runbooks/session-handoff-protocol.md)
- 批量执行：[batch-ai-execution-runbook.md](./runbooks/batch-ai-execution-runbook.md)
- 任务分级：[task-levels.md](./task-levels.md)
- 完成定义：[completion-criteria.md](./completion-criteria.md)
- 验证基线：[verification-baseline.md](./verification-baseline.md)
