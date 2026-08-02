# AI 跨 Session、多 Agent 协作与 Dogfood 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development`（推荐）或 `executing-plans` 逐任务实施；每个演练任务必须由独立评审门禁验收。

**Goal:** 建立不依赖聊天历史的 Session 接力协议、受控并行 AI 执行流程和真实任务反馈闭环。

**Architecture:** Session Handoff 是角色切换的持久化接口，Task Packet 是并行工作的边界声明，Integration Owner 独占共享文件和最终集成。Summary 仅提供快速入口，完整规范仍是唯一权威来源；Dogfood 报告只记录证据和改进建议，不自动升级规则。

**Tech Stack:** Markdown、现有 doctor/链接检查/一致性检查、Git worktree、项目 verify 入口

## Global Constraints

- 前置条件：规则收敛、自动守卫与验证分层两个计划均已完成。
- 本计划属于 L3 治理变更，实施前必须获得明确批准。
- 新 Session 必须能仅凭仓库交付物恢复状态，不依赖对话历史。
- 并行 agent 不得同时修改共享文件；共享文件由 Integration Owner 独占。
- Summary 不得创造新规则，只能引用权威来源。
- Dogfood 至少覆盖 L0、L1、L2；结果不自动成为硬门禁。

---

## 文件职责与变更范围

- Create: `docs/ai/runbooks/session-handoff-protocol.md` — Handoff schema、落盘位置和阶段门禁。
- Create: `docs/ai/runbooks/batch-ai-execution-runbook.md` — 并行拆分、文件所有权、集成和失败隔离。
- Modify: `docs/ai/templates/task-packet.md` — owned/shared/prohibited paths 与依赖字段。
- Modify: `docs/ai/templates/feature-spec.md` — Session 状态和 handoff 引用。
- Modify: `docs/ai/templates/implementation-plan.md` — integration owner 与验证责任。
- Modify: `docs/ai/runbooks/l2-multi-session-runbook.md` — 每阶段读写 Handoff。
- Modify: `docs/ai/context-index.md` — Handoff 和 batch 入口。
- Modify: `docs/ai/completion-criteria.md` — 接力完整性和批量集成条件。
- Create: `docs/ai/task-levels-summary.md` — 任务等级短路径。
- Create: `docs/ai/branch-strategy-summary.md` — 分支与隔离短路径。
- Create: `docs/ai/context-index-summary.md` — 新 Session 三分钟入口。
- Create: `docs/ai/commit-convention.md` — commit 单点规范。
- Create: `docs/ai/commit-convention-summary.md` — commit 快速摘要。
- Modify: `AGENTS.md`, `template/AGENTS.md` — 新入口链接。
- Create: `docs/ai/dogfood/README.md` — 演练记录格式和保留策略。
- Create: `docs/ai/dogfood/2026-08-ai-governance-v2-report.md` — 三类真实演练证据。

### Task 1：定义结构化 Session Handoff Protocol

**Produces:** 规划、实施、评审 Session 之间稳定的仓库内接口。

- [ ] 创建 `session-handoff-protocol.md`，定义以下必填 schema：

```md
## Session Handoff

- Task Level: L2
- Current Phase: planning | implementation | review
- Status: ready | blocked | completed
- Completed:
- Artifacts:
- Decisions:
- Assumptions:
- Open Questions:
- Verification:
- Next Allowed Actions:
- Prohibited Scope:
```

- [ ] 明确物理落点：L2 规划结束写入 plan 末尾；实施结束更新同一 plan 的 Handoff 并在验证证据中记录命令；评审结果写入 plan 的 review 段或独立 review report，并回链 plan。

- [ ] 定义门禁：必填字段缺失、状态为 blocked、artifact 不存在或 verification 与当前阶段不匹配时，下一 Session 必须停止。

- [ ] 更新 L2 runbook 和三个模板，加入准确链接及字段，不复制 schema 全文。

- [ ] 静态验收：

```bash
rg -n 'Task Level|Current Phase|Status|Artifacts|Verification|Next Allowed Actions|Prohibited Scope' \
  docs/ai/runbooks/session-handoff-protocol.md
python3 scripts/check-markdown-links.py --root . --template
python3 scripts/check-governance-consistency.py --root . --template
```

Expected: schema 七类核心字段均有匹配；检查器退出 0。

### Task 2：定义 Batch AI Execution Runbook

**Interfaces:**
- Consumes: Session Handoff schema、task packet、Verification Profile。
- Produces: 可并行性判定和 Integration Owner 责任模型。

- [ ] 创建 batch runbook，规定只有满足以下条件才可并行：任务无顺序依赖、owned paths 不重叠、无需同时修改共享配置、可独立验证。

- [ ] 定义 task packet 新字段：

```md
- Owner:
- Owned Paths:
- Shared Paths:
- Prohibited Paths:
- Depends On:
- Local Verify:
- Integration Owner:
- Integration Verify:
```

- [ ] 定义冲突处理：任何 shared path 只能由 Integration Owner 修改；子 agent 只能提交建议或 patch 说明，不得直接落盘共享文件。

- [ ] 定义失败隔离：单任务失败不合并；其他独立任务可继续；依赖失败任务的任务转 blocked；最终 full verify 失败则整批不得声明完成。

- [ ] 更新 completion criteria 和 context index。

- [ ] 通过三任务纸面演练验证：A/B owned paths 不重叠可并行，C 修改共享文件必须交给 Integration Owner；将示例写入 runbook 的完整示例段。

- [ ] 运行：

```bash
python3 scripts/check-markdown-links.py --root . --template
python3 scripts/check-governance-consistency.py --root . --template
git diff --check
```

Expected: 全部退出 0。

### Task 3：增加快速摘要层

**Produces:** 新 Session 的低上下文入口，不改变规范语义。

- [ ] 创建三个 summary，每份控制在约 80 行内，只包含：适用场景、决策表、停止条件、权威来源链接。

- [ ] `task-levels-summary.md` 覆盖 L0-L3 判定、所需交付物和升级条件。

- [ ] `branch-strategy-summary.md` 覆盖 main 保护、worktree 要求和 Strict Isolation Profile。

- [ ] `context-index-summary.md` 提供 L0/L1 短路径、L2/L3 深路径和 Session Handoff 恢复路径。

- [ ] 在每份顶部加入：

```md
> 本文仅为快速摘要；如有冲突，以链接的权威规范和 Accepted ADR 为准。
```

- [ ] 更新 `AGENTS.md` 和 `template/AGENTS.md`，优先链接 summary，再链接完整规范。

- [ ] 对比摘要和权威来源中的关键数字：

```bash
rg -n '3 个 session|4 个 session|L0|L1|L2|L3' docs/ai/*summary.md docs/ai/task-levels.md docs/ai/branch-strategy.md
```

Expected: Session 数量和等级要求一致。

### Task 4：建立 Commit Convention 单点

**Produces:** 人工与 AI 共享的提交边界和证据规则。

- [ ] 创建完整规范，至少定义：Conventional Commit type 白名单、scope 可选/必需规则、描述格式、breaking change、AI 默认不自动 commit、不得跳过 hooks、不得 amend 未明确授权的提交。

- [ ] 定义推荐提交边界：spec、plan、implementation、review follow-up 可以分提交；不得为了“提交整齐”混入无关修改。

- [ ] 定义 PR/MR 描述最小字段：目标、范围、非目标、验证证据、风险/回滚、关联 spec/plan。

- [ ] 创建 summary，并从 `AGENTS.md`、`template/AGENTS.md`、review checklist 链接到完整规范。

- [ ] 验证：

```bash
rg -n 'feat|fix|docs|refactor|test|build|ci|chore|不得.*自动.*commit|验证证据|回滚' \
  docs/ai/commit-convention.md
python3 scripts/check-markdown-links.py --root . --template
```

Expected: 所有核心约束有匹配，链接检查退出 0。

### Task 5：建立 Dogfood 记录机制

- [ ] 创建 `docs/ai/dogfood/README.md`，定义记录字段：任务、等级判定、实际耗时、交付物、运行命令、失败/绕过、规则歧义、建议；禁止记录 token、密码、`.env` 内容和内部凭据。

- [ ] 选择三个真实且范围受控的后续任务：

```text
L0：单文件文档 typo 或链接文本修正。
L1：doctor 的单目标检查改进，带 task packet 和局部测试。
L2：新增一项独立治理检查，走规划 / 实施 / 评审三 Session。
```

- [ ] 每个任务开始前记录等级和依据，结束后记录真实命令、退出码与关键输出，不使用预期结果替代实际结果。

- [ ] 将结果汇总到 `2026-08-ai-governance-v2-report.md`，按以下指标评估：分级一致性、worktree 摩擦、handoff 恢复成功率、verify 耗时、规则歧义数量、被自动守卫捕获的问题数。

- [ ] 只提出改进建议；任何新硬门禁必须另开 spec/plan 和 L3 批准，不在 dogfood 报告内直接修改规则。

### Task 6：全链路演练与最终验收

- [ ] 模拟一次 L2 接力：规划 Session 生成双文件和 Handoff；新实施 Session 仅读取仓库文件恢复；评审 Session 消费 diff、验证证据和 Handoff。

- [ ] 模拟一次三任务 batch：两个独立任务并行，一个 shared path 任务由 Integration Owner 处理；记录局部验证和最终 full verify。

- [ ] 验证所有新增文档：

```bash
python3 scripts/check-markdown-links.py --root . --template
python3 scripts/check-governance-consistency.py --root . --template
bash scripts/scaffold-doctor.sh --template
git diff --check
```

Expected: 全部退出 0，doctor `0 fail(s)`。

- [ ] 请求独立评审，重点检查：Handoff 能否脱离聊天历史、文件所有权是否排除并行冲突、Summary 是否引入新规则、Dogfood 是否包含真实证据。

- [ ] 用户确认后按逻辑分组提交，不自动提交：

```bash
git add docs/ai/runbooks/session-handoff-protocol.md docs/ai/runbooks/batch-ai-execution-runbook.md \
  docs/ai/templates docs/ai/context-index.md docs/ai/completion-criteria.md
git commit -m "docs(ai): add session handoff and batch execution protocols"
git add docs/ai/*summary.md docs/ai/commit-convention*.md AGENTS.md template/AGENTS.md
git commit -m "docs(ai): add governance summaries and commit convention"
git add docs/ai/dogfood
git commit -m "docs(ai): record governance workflow dogfood results"
```
