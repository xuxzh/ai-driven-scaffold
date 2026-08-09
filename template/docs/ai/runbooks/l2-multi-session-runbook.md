# L2 三 Session 串行工作流（通用）

> **本运行手册定义 L2 任务通用的 3 Session 串行纪律**——所有 L2 任务类型（功能、缺陷修复、重构）共享。
>
> **任务类型特定差异** 参见：
> - 功能（feature）：[feature-delivery-runbook.md](./feature-delivery-runbook.md)
> - 缺陷修复：[bugfix-delivery-runbook.md](./bugfix-delivery-runbook.md)
> - 重构：[refactor-delivery-runbook.md](./refactor-delivery-runbook.md)
>
> **L3 任务的 4 Session 串行**：在 L2 三 Session（规划 / 实施 / 评审）的基础上，将"规划"再拆分为"设计 + 计划"双 Session；总计 4 个 Session，并在实施 session 启动前收用户"已批准"信号（详见 [ADR-0003](../../adr/0003-multi-session-l2.md) 与 [ADR-0005](../../adr/0005-l3-approval-gate.md)）。

## 目的

本文档定义 L2 任务在仓库内如何按 3 个独立 session 串行完成规划、实施和评审。

**默认目标不是让 AI 在一个 session 内生成完整代码**，而是让 AI 在明确边界内受控执行，每 session 留下可回看的交付物与验证证据，下一 session 从仓库文档接力（详见 [ADR-0003](../../adr/0003-multi-session-l2.md)）。

## 适用范围

L2 任务。本文档定义通用纪律；任务类型特定内容由各 task-type runbook 给出。

L0 / L1 任务可单 session 串完——多 session 是 L2+ 的入场费，不向下传递。

L3 任务将 L2 的"规划 Session"再拆为"设计 + 计划"双 Session，并叠加实施前批准门禁；总计 4 个 Session；详见 [ADR-0003](../../adr/0003-multi-session-l2.md) 的"L3 四 Session"段。

## 总体原则

- **会话边界 = 角色边界**：3 个 session 串行，不允许单 session 串完全部角色
- **规划 session 内先 spec 后 plan**：spec 与 plan 始终是两份独立文件；spec 必须先经用户确认，plan 才允许落字
- **每 session 结束前**输出"本 session 完成信号"+ 交付物路径，让下一 session 从仓库接力
- **用户可见行为必须有验证证据**（继承 [ADR-0002](../../adr/0002-verify-hard-gate.md)）
- **AI 汇报时必须说明**：实际运行了哪些命令、哪些通过、哪些未运行及原因

## 任务分级

L2 任务的适用情形详见 [task-levels.md](../task-levels.md) 与 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)。L2 走通用 3 Session（规划 / 实施 / 评审）；L3 在 L2 之上把"规划 Session"再拆为"设计 + 计划"双 Session 并叠加 [ADR-0005](../../adr/0005-l3-approval-gate.md) 的 Pre-Implementation Approval Gate，总计 4 个 Session。

如果需求触及鉴权、权限模型、部署、CI、依赖升级、跨 workspace 重构或仓库级默认约定，应提升为 `L3`，由人工主导并在实施 session 启动前收用户明确批准。

## 3 Session 串行总览

> **verify 落点（统一）**：spec 与 plan 双份**各自末尾**的 `## 验证证据` 段是 verify 报告的唯一落点；规划 session **不**跑 verify、**不**写 `## 验证证据` 段；实施 session 必须跑项目根目录 `verify`、把退出码 / 关键输出 / 未跑项写回到 spec 与 plan 两份文件的 `## 验证证据` 段（详见 [ADR-0002](../../adr/0002-verify-hard-gate.md) 与下文"verify 落点细则"）。

| Session | 角色 | 必读输入 | 必交付物 | 必跑 verify |
|---|---|---|---|---|
| **规划** | 设计辅助者 + 计划拆解者 | AGENTS.md + context-index + task-levels + 接口/UI 文档 | `docs/specs/<date>-<name>.md`（仅 spec）→ 用户确认 → `docs/plans/<date>-<name>.md`（仅 plan）；不写 `## 验证证据` 段；按 [`session-handoff-protocol.md`](./session-handoff-protocol.md) 在 plan 末尾写 Handoff | **不要求**（规划 session 仅接力交付物） |
| **实施** | 实施者 + 文档维护者 | 上一 session 的 spec + plan 双份 | 代码 + 测试 + spec 与 plan 双份末尾的 `## 验证证据` 段；更新同一 plan 的 Handoff | **必须**跑 `verify` 并写回两份 `## 验证证据` |
| **评审** | 审查者（**默认新开 session**） | 实施交付物 + 不读实施 session 中间对话 | review report（按 [review-checklist.md](../checklists/review-checklist.md)）；验证 `## 验证证据` 段双份齐；按协议写 plan review 段或独立 report 回链 plan | 含"测试盲区"清单 |

L3 任务在"实施 session 启动前"增加一道门：必须先收用户"已批准"信号，详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)。

> 路径命名（`<date>-<name>.md`）与文件顶部 `## 元信息` 段规范见 [spec-and-plan-naming.md](../spec-and-plan-naming.md)；本 runbook 内所有 `docs/specs/...` / `docs/plans/...` 路径占位符均按此命名。

> **已取代**：本 runbook 早前版本的 4 Session 表（设计 / 计划 / 实施 / 评审）与"快速通道（小 L2 例外）"段已被 [ADR-0003](../../adr/0003-multi-session-l2.md) 2026-08-01 修订取代。**L2 现行规则是 3 Session；spec 与 plan 始终物理分离，不存在豁免合并的现行例外。** L3 保持 4 Session + 实施前批准门禁。

---

## 第 1 Session：规划（设计辅助者 + 计划拆解者）

**目标**：把需求转化为仓库内可执行的 spec，并在此基础上产出可执行 plan；spec 与 plan 始终是两份独立文件。

**必读入口**：

- `AGENTS.md`
- `docs/ai/context-index.md`
- `docs/ai/task-levels.md`
- `docs/adr/0004-l2-spec-and-plan.md`（spec / plan 内容分工）
- 项目自身的接口/UI 规范（如有）

### 步骤 1：先写 spec

**必交付物**：`docs/specs/<date>-<name>.md`，按对应模板填写：

- 功能：[feature-spec.md](../templates/feature-spec.md)
- 缺陷修复：[bugfix-brief.md](../templates/bugfix-brief.md)
- 重构：[refactor-brief.md](../templates/refactor-brief.md)

**spec 必含字段**：

- 背景、目标、非目标
- 受影响边界（路由 / 数据流 / 状态 / 共享组件 / 工具链）
- 备选方案与拒绝理由
- 风险与未决问题
- 验证计划（**总体策略**，具体命令留给 plan）

### 步骤 2：等用户确认 spec

- spec 落地后，AI 必须**显式停下**，等用户对 spec 的明确确认（"已确认 spec" / "approved" / "继续 plan" / "proceed" 等任一字眼）
- 缺信号时 AI **不得**开始写 plan——plan 必须等 spec 确认后才能落字
- 评审 session 必查"spec 是否先经用户确认、plan 是否在 spec 确认之后才落字"

### 步骤 3：再写 plan

- 确认 spec 后，写 `docs/plans/<date>-<name>.md`，按 [implementation-plan.md](../templates/implementation-plan.md) 模板填写
- plan 抬头必须：

```markdown
> 基于 spec：[docs/specs/<date>-<name>.md](...)
```

否则视为与 spec 失联（详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)）。

**plan 必含字段**：

- 文件清单（新建 / 修改 / 测试）
- 任务切片（按可验证切片拆分）
- 每切片：步骤 / 命令 / 预期结果
- 验收标准
- 明确不做什么

### 规划 session 输出信号

本 session 末尾输出一段"规划 session 完成，交付物：spec at <spec-path> + plan at <plan-path>"。

### 规划 session 不允许

- 写代码或修改业务文件
- 跳过 spec 确认直接写 plan
- 把 spec 与 plan 物理合并为一份文件（spec + plan 始终是两份独立文件）
- 写 verify 报告（验证由实施 session 跑）

### 规划 session 完成后人工检查

- spec 的目标是否准确、非目标是否足够明确
- plan 的切片是否独立可验证
- 是否存在 AI 自行扩大范围
- spec 与 plan 物理分离（两份独立文件）、plan 抬头是否引用 spec 路径
- 未决问题是否需要先问业务或后端

---

## 第 2 Session：实施（实施者 + 文档维护者）

**目标**：按 plan 切片逐步实施，每切片完成即跑对应验证；实施 session 末尾跑 `verify` 并把结果**同时**写入 spec 与 plan 双份末尾的 `## 验证证据` 段。

**L3 任务的前置条件**：必须先收用户"已批准"信号（"已批准" / "approved" / "proceed" / "go-ahead" / "确认执行" 任一字眼）并引用 spec/plan 双份路径。**缺信号时 AI 不得跑 `git add` / `git commit` / 直接 patch / 创建 MR / 直接 push**（详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)）。

**必读入口**：

- 上一 session 产出的 spec + plan 双份
- `docs/ai/branch-strategy.md`（分支 / worktree 选择）
- 项目根目录的 `verify` 命令

**必交付物**：

- 按 plan 切片实施的代码 + 测试
- `docs/specs/<date>-<name>.md` **与** `docs/plans/<date>-<name>.md` 双份末尾的 `## 验证证据` 段（两份均必填，**不**接受"只写 spec 或只写 plan"，详见下文"verify 落点细则"）

**必跑 verify**（继承 [ADR-0002](../../adr/0002-verify-hard-gate.md)）：

- 实施 session 末尾**必须**跑项目根目录的 `verify` 入口
- 把命令的实际退出码与关键输出摘要**同时**写入 spec 与 plan 两份文件的 `## 验证证据` 段
- 未跑项必须显式标注原因
- 缺 verify 报告或仅单份文件落字**不能**声明完成

### verify 落点细则（统一）

**唯一落点**：`docs/specs/<date>-<name>.md` **与** `docs/plans/<date>-<name>.md` 双份末尾的 `## 验证证据` 段。两份均必填，**不**接受只填其中一份：

| Session | 是否跑 verify | 是否写 `## 验证证据` 段 | 写哪份文件 |
|---|---|---|---|
| **规划** | 不跑 | 不写（保持模板空白） | 无；交接下一 session |
| **实施** | **必须**跑项目根目录 `verify` | **必须**写 | spec 与 plan 双份均写 |
| **评审** | 不需要重跑（除非复测） | 不写（只审 `## 验证证据` 段是否齐） | 验证 spec 与 plan 双份均已落字 |

- **不允许**"只填 spec 或只填 plan"——任何"只填一份"视为 verify 报告未完整
- **不允许**"写在分支评论 / 外部文档 / 评审 session 笔记中代替"——`## 验证证据` 段是事实落字的唯一载体
- **不允许**"实施 session 没跑 verify、但后一 session 补跑"——verify 是实施 session 的责任，跨 session 移交视为未跑

### `## 验证证据` 段格式示例

```markdown
## 验证证据

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `<pm> lint` | 0 | "All checks passed" | |
| `<pm> typecheck` | 0 | "No errors" | |
| `<pm> test` | 0 | "42 passed" | |
| `<pm> test:e2e` | 0 | "5 passed" | |
| `<pm> build` | 0 | "Build complete" | |
| `<pm> verify` | 0 | "All steps passed" | 完整基线 |

未跑项：`<pm> test:e2e` 在 CI 中跑；本机环境无 headless browser。
```

**L3 任务追加要求**：spec 与 plan 两份文件均在 `## 验证证据` **之前**增加 `## 批准` 段（含 [ADR-0005](../../adr/0005-l3-approval-gate.md) 第 8 项最小必含），模板顺序为：

```markdown
## 批准（必填；spec / plan 双份均加）

- 批准时间：YYYY-MM-DD
- 批准信号：（包含"已批准"等关键字眼）
- 批准来源：<issue-link> / <PR-link> / 会话消息引用
- spec 路径：`[docs/specs/<date>-<name>.md](...)`
- plan 路径：`[docs/plans/<date>-<name>.md](...)`
- 允许修改范围：（与 spec `## 目标` / `## 行为` / `## 非目标` 对齐）
- 禁止范围：明确列出本次不批准的事项（如新依赖、新文件、新接口扩展等）

## 验证证据（实施 session 末尾必填；spec / plan 双份均加）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |

未跑项：
```

**必输出信号**：本 session 末尾输出"实施 session 完成，交付物：code at <branch> + 验证证据 at <spec-path>#验证证据 与 <plan-path>#验证证据 双份均齐"。

---

### Session Handoff 落地说明

每个 Session 结束前，按 [`session-handoff-protocol.md`](./session-handoff-protocol.md) 填写或更新物理 Handoff；下一 Session 开始先执行协议门禁，门禁失败必须停止。

## 第 3 Session：评审（审查者，默认新开 session）

**目标**：以独立视角审查实施 session 的交付物，找出行为回归、边界破坏、验证缺失、测试缺口、风格问题。

**必读入口**：

- 上一 session 产出的代码 + spec + plan + `## 验证证据` 段
- `docs/ai/checklists/review-checklist.md`（评审清单）
- `docs/adr/0002-verify-hard-gate.md`（verify 必跑纪律检查）

**建议**：

- **默认新开 session**，从零上下文进入
- **不**预读实施 session 的中间对话；只读 `git diff <base>..HEAD`、spec、plan、`## 验证证据` 段
- 这样可以避免实施 session 的合理化路径污染评审判断

**必交付物**：review report（按 [review-checklist.md](../checklists/review-checklist.md) 结构），**必含**：

- 严重级别 + 文件 + 行为位置 + 风险说明 + 缺失的验证或测试
- "测试盲区"清单（评审者**必填**，未发现也明确写"未发现 + 剩余风险"）
- "未跑项"清单（对照 `## 验证证据` 段的未跑项逐一确认是否被说明）
- 对 L2 规划的额外检查：spec 与 plan 是否物理分离、spec 是否先经用户确认、plan 抬头是否引用 spec 路径

**必输出信号**：本 session 末尾输出"评审 session 完成，交付物：review report at <path>"。

**评审者不应**：

- 继续扩写功能
- 修改代码（修改代码是实施 session 的事）
- 给出空泛通过结论

---

## 完成定义

L2 任务完成判据的通用五项见 [completion-criteria.md](../completion-criteria.md)；以下为 L2 三 session 串联视角的增量条件：

- 3 个 session 的交付物都在仓库内（spec、plan、代码、`## 验证证据`、`review report`）
- spec 与 plan **物理分离**（两份独立文件），spec 先经用户确认、plan 抬头引用 spec 路径
- 实施 session 跑过 `verify` 且结果**同时**写入 spec 与 plan 双份的 `## 验证证据` 段；规划 session 未写 `## 验证证据`（保持模板空白）；不允许"只填一份"
- `## 验证证据` 段的填写顺序：L3 任务须保证 `## 批准` 段位于 `## 验证证据` 段之前
- `## 批准` 段（L3 必填）按 [ADR-0005](../../adr/0005-l3-approval-gate.md) 第 8 项最小必含；不得跨任务复用
- review report 含"测试盲区"清单
- 触及长期约定时文档已同步更新
- 未执行的验证有明确原因和残余风险说明

L3 任务在上述条件之外，还必须满足 [ADR-0005](../../adr/0005-l3-approval-gate.md) 的批准范围未扩张（批准信号 + spec/plan 双份路径 + 允许修改范围 + 禁止范围 + `## 批准` 段已留痕；批准仅约束当次任务，不跨任务复用）。

> **已取代**：本 runbook 早前版本包含"快速通道（小 L2 例外）"段，允许 L2 任务规模 < 半天时合并 spec/plan 物理分离。**该例外已被 [ADR-0003](../../adr/0003-multi-session-l2.md) 2026-08-01 修订显式废止**——spec 与 plan 物理分离是 L2 的硬门禁，不存在规模豁免；现行规则为 L2 三 Session 且 spec 与 plan 始终物理分离。

## 任务类型特定差异

各任务类型（功能、缺陷修复、重构）有各自的推荐切片顺序、注意事项和禁区，详见对应的 runbook：

- 功能：[feature-delivery-runbook.md](./feature-delivery-runbook.md)
- 缺陷修复：[bugfix-delivery-runbook.md](./bugfix-delivery-runbook.md)
- 重构：[refactor-delivery-runbook.md](./refactor-delivery-runbook.md)

## 不属于本文范围

- 任务分级的判定条件与 `L0` / `L1` / `L2` / `L3` 等级矩阵：见 [task-levels.md](../task-levels.md)
- 完成判据的通用五项：见 [completion-criteria.md](../completion-criteria.md)
- verify 必跑 + 必汇报的硬门禁依据：见 [ADR-0002](../../adr/0002-verify-hard-gate.md)
- session 数与序列的权威定义（`L2` 三 session / `L3` 四 session）：见 [ADR-0003](../../adr/0003-multi-session-l2.md)
- spec / plan 内容分工与物理分离硬门禁：见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)
- `L3` 批准门禁的最小必含项：见 [ADR-0005](../../adr/0005-l3-approval-gate.md)
- 任务类型特定差异（feature / bugfix / refactor）：见对应 delivery runbook

本文只承载 `L2` 三 session 的串联纪律与 verify 落点操作细则；通用规则不在此复述。

## 关联

- 治理基线：[../governance-core.md](../governance-core.md)
- 任务分级：[../task-levels.md](../task-levels.md)
- ADR：[../../adr/0003-multi-session-l2.md](../../adr/0003-multi-session-l2.md)
- AI 角色边界：[../ai-role-boundaries.md](../ai-role-boundaries.md)
