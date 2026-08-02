# AI 治理规则收敛实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development`（推荐）或 `executing-plans` 逐任务实施；使用复选框跟踪进度。

**Goal:** 消除任务等级、分支隔离和多 Session 规则之间的矛盾，形成单点定义、可被 AI 一致执行的治理基线。

**Architecture:** `AGENTS.md` 只承载入口级硬规则，`docs/ai/` 承载规范单点，ADR 记录决策理由，runbook 描述执行步骤，模板只引用这些权威来源。L2 使用“规划 / 实施 / 评审”三 Session 且保持 spec/plan 物理分离；L3 保持四 Session与实施前批准门禁。

**Tech Stack:** Markdown、Bash、现有 `scripts/scaffold-doctor.sh`

## Global Constraints

- 本计划属于 L3 仓库级治理变更，实施前必须获得用户明确批准。
- 在独立 worktree 和合规任务分支中实施，不在 `main` / `master` 落盘。
- 只调整通用治理规则，不复制 `report-platform` 的业务 ADR。
- 不引入新运行时或第三方依赖。
- 保持 `docs/specs/` 与 `docs/plans/` 两份 L2 交付物物理分离。
- 每项文档规则必须只有一个权威定义，其余位置使用摘要和链接。

---

## 文件职责与变更范围

- Modify: `AGENTS.md` — Scaffold 自身入口级硬规则及 Adoption Profile。
- Modify: `template/AGENTS.md` — 接入目标项目的可填写入口模板。
- Modify: `docs/ai/task-levels.md` — L0-L3 分级和各级准入条件的单点定义。
- Modify: `docs/ai/branch-strategy.md` — 分支、主工作区、worktree 隔离策略单点。
- Modify: `docs/ai/ai-role-boundaries.md` — 三/四 Session 的角色边界。
- Modify: `docs/ai/context-index.md` — 按任务等级和 Session 角色提供阅读路径。
- Modify: `docs/ai/completion-criteria.md` — 完成条件与证据要求。
- Modify: `docs/ai/governance-core.md` — 治理总览和权威来源索引。
- Modify: `docs/ai/runbooks/l2-multi-session-runbook.md` — L2 三 Session 执行流程。
- Modify: `docs/ai/runbooks/development-runbook.md` — 通用开发流程入口。
- Modify: `docs/ai/runbooks/{feature,bugfix,refactor}-delivery-runbook.md` — 专项流程引用。
- Modify: `docs/ai/templates/feature-spec.md` — spec 必填字段。
- Modify: `docs/ai/templates/implementation-plan.md` — plan 必填字段及 spec 反向引用。
- Modify: `docs/adr/0001-task-level-governance.md` — 任务分级决策。
- Modify: `docs/adr/0003-multi-session-l2.md` — L2 三 Session、L3 四 Session 决策。
- Modify: `docs/adr/0004-l2-spec-and-plan.md` — 双文件交付决策。
- Modify: `docs/adr/0005-l3-approval-gate.md` — L3 批准范围。
- Modify: `docs/ai/checklists/{adoption,review}-checklist.md` — 接入和评审检查项。

### Task 1：建立规则冲突基线

**Produces:** 可复现的冲突清单，作为后续修改的验收基准。

- [ ] 运行以下搜索并保存终端结果，不新增文档：

```bash
rg -n 'L0.*main|main.*L0|L2\+.*4 个 session|设计 / 计划 / 实施 / 评审|快速通道|推荐.*worktree|优先.*worktree' \
  AGENTS.md template/AGENTS.md docs/ai docs/adr
```

- [ ] 确认至少能定位当前已知冲突：`docs/ai/task-levels.md` 的 L0 主分支例外、L2+ 四 Session 和快速通道物理合并规则。

- [ ] 运行基线 doctor：

```bash
bash -n scripts/scaffold-doctor.sh
bash scripts/scaffold-doctor.sh --template
```

Expected: `0 fail(s)`；允许模板模式下现有 WARN。

### Task 2：统一任务等级与隔离策略

**Interfaces:**
- Produces: L0-L3 的唯一等级矩阵，供 runbook、模板和后续自动检查消费。

- [ ] 修改 `docs/ai/task-levels.md`，使用以下统一语义：

```text
L0：单文件、不跨模块、不改变默认行为；无需 packet/spec/plan；至少运行最小验证。
L1：单目标常规改动；task packet 先行；任务分支 + 独立 worktree。
L2：跨文件行为、数据流或入口变化；spec + plan 双文件；任务分支 + 独立 worktree。
L3：CI、依赖、安全、鉴权、仓库级约定；人工主导；L2 条件 + 实施前明确批准。
```

- [ ] 修改 `docs/ai/branch-strategy.md`，明确区分：工作区落盘、分支、提交、worktree；默认策略为 L0 任务分支但 worktree 可选，L1+ 强制独立 worktree。

- [ ] 在 `docs/ai/branch-strategy.md` 增加 `Strict Isolation Profile`：接入项目可声明所有等级强制 worktree；启用后不得保留 L0 例外。

- [ ] 更新 `AGENTS.md` 与 `template/AGENTS.md`，只保留上述矩阵的短摘要和权威链接，不重新发明条件。

- [ ] 运行冲突搜索：

```bash
rg -n 'L0 可在.*main|L2.*推荐.*worktree|L3.*推荐.*worktree' \
  AGENTS.md template/AGENTS.md docs/ai docs/adr
```

Expected: 无匹配；若引用历史决策，必须明确标记为“已取代”，不得作为现行规则。

### Task 3：将 L2 收敛为三 Session

**Interfaces:**
- Consumes: Task 2 的任务等级矩阵。
- Produces: L2 三 Session / L3 四 Session 的唯一角色模型。

- [ ] 修改 `docs/adr/0003-multi-session-l2.md`，记录决策：L2 为规划、实施、评审三个 Session；L3 为设计、计划、实施、评审四个 Session。

- [ ] 修改 `docs/ai/ai-role-boundaries.md`：规划者只产出 spec 和 plan，不修改业务代码；实施者只消费已确认交付物；评审者不承担首轮实现。

- [ ] 修改 `docs/ai/runbooks/l2-multi-session-runbook.md`，将执行表改为：

```text
规划：先写 docs/specs/<date>-<name>.md；用户确认后写 docs/plans/<date>-<name>.md。
实施：读取 spec + plan，实施、测试并记录验证证据。
评审：读取 diff + spec + plan + 验证证据，输出审查结论。
```

- [ ] 删除“快速通道允许 spec/plan 物理合并”的规则；小 L2 只能合并规划对话步骤，不能合并两份文件。

- [ ] 同步 development/feature/bugfix/refactor runbook、context index 和 completion criteria。

- [ ] 搜索残留：

```bash
rg -n 'L2\+.*4 个 session|L2.*设计 / 计划 / 实施 / 评审|只豁免 spec 与 plan 的物理分离' \
  AGENTS.md template/AGENTS.md docs/ai docs/adr
```

Expected: 无现行规则匹配。

### Task 4：强化双文件交付和 L3 批准范围

- [ ] 修改 `docs/adr/0004-l2-spec-and-plan.md`，明确两份文件的最小接口：spec 定义目标、行为、非目标和验收；plan 定义文件、步骤、验证和回滚，并链接 spec。

- [ ] 修改两个模板：spec 不包含逐步实现清单；plan 顶部必须包含精确 spec 路径。

- [ ] 修改 `docs/adr/0005-l3-approval-gate.md`，批准记录必须包含：批准信号、spec 路径、plan 路径、允许修改范围、禁止范围；批准不得跨任务复用。

- [ ] 更新 review checklist，加入“交付物物理分离”和“批准范围未扩张”。

- [ ] 验证模板字段：

```bash
rg -n '目标|非目标|验收' docs/ai/templates/feature-spec.md
rg -n '基于 spec|文件|验证|回滚' docs/ai/templates/implementation-plan.md
```

Expected: 两条命令均找到对应必填段。

### Task 5：修复链接并完成一致性验收

- [ ] 修复 `docs/ai/runbooks/l2-multi-session-runbook.md` 中命名规范链接为：

```md
[spec-and-plan-naming.md](../spec-and-plan-naming.md)
```

- [ ] 检查所有本次修改的 Markdown 相对链接，至少确认链接目标存在：

```bash
python3 - <<'PY'
from pathlib import Path
assert Path('docs/ai/spec-and-plan-naming.md').is_file()
assert Path('docs/adr/0003-multi-session-l2.md').is_file()
assert Path('docs/ai/templates/feature-spec.md').is_file()
assert Path('docs/ai/templates/implementation-plan.md').is_file()
print('PASS governance targets exist')
PY
```

- [ ] 运行最终验证：

```bash
bash -n scripts/scaffold-doctor.sh
bash scripts/scaffold-doctor.sh --template
git diff --check
git status --short
```

Expected: doctor `0 fail(s)`；`git diff --check` 退出码 0；状态仅包含本计划列出的治理文件。

- [ ] 请求独立代码/文档评审，重点检查规则单点、矛盾、链接和范围漂移。

- [ ] 经用户确认后按逻辑分组提交；不要自动提交：

```bash
git add AGENTS.md template/AGENTS.md docs/ai docs/adr
git commit -m "docs(ai): consolidate governance workflow rules"
```
