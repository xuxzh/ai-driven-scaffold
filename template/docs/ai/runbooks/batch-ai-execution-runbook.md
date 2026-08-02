# 批量 AI 执行运行手册（Batch AI Execution Runbook）

> **本文档定义"一次规划 / 多次并行实施 / 单点集成"的可控协作纪律**——决定任务是否可以并行、文件所有权如何分配、共享文件由谁独占、单任务失败如何隔离。
>
> **本 runbook 适用场景**：单次 L2 实施或 L3 实施需要把"按 spec/plan 落地"切分为多个子任务、由多个 agent 协作完成，且仍希望保留"会话边界 = 角色边界 + 接力完整性"的纪律。
>
> **本 runbook 不适用**：L0 / L1 单文件改动（无需多 agent）、需要严格 L2 三 Session 串行的小 L2 任务（直接走 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)）。

## 目的

把 L2+ 任务切成多个子任务交给多个 agent 并行实施时，本 runbook 规定：

- 哪些子任务**可以**并行（可并行判定）
- 每个子任务**拥有**哪些文件（Owned Paths）
- 哪些文件是**共享**的、只允许 Integration Owner 修改（Shared Paths）
- 子 agent **不得**触碰哪些文件（Prohibited Paths）
- 子任务之间**依赖**关系如何表达
- 集成阶段**由谁**负责最终合并 + 跑 `full verify`（Integration Owner）
- **单任务失败**如何不污染整批（失败隔离）

它**不**重新定义 L2 三 Session、L3 四 Session、verify 必跑或 Pre-Implementation Approval Gate——这些仍由 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)、[ADR-0002](../../adr/0002-verify-hard-gate.md)、[ADR-0003](../../adr/0003-multi-session-l2.md) 与 [ADR-0005](../../adr/0005-l3-approval-gate.md) 承担；本 runbook 在其上叠加"多 agent 并行"的责任模型。

## 适用范围

- **L2 实施阶段** 当 plan 含 ≥3 个相对独立切片、且切片间无顺序依赖时，可按本 runbook 拆给多个 worker agent 并行落地
- **L3 实施阶段** 在 L2 之上叠加 Pre-Implementation Approval Gate（详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)），其余并行纪律一致
- **不**用于 L0 / L1（无并行收益）
- **不**用于评审 session（评审 session 默认新开、走 [review-checklist.md](../checklists/review-checklist.md)）
- **不**用于 L2 规划 session（规划 session 必须串行单 agent；并行不替代"先 spec → 用户确认 → 再 plan"的硬门禁）

## 总体原则

- **可并行 = 4 条件全满足**；缺一则降级为串行（走 L2/L3 默认的 3/4 Session 流程）
- **每个子任务 = 一份完整 task packet**（按 [task-packet.md](../templates/task-packet.md)）；packet 中的 8 个批量子字段（见下文"8 字段 schema"）全部必填
- **Owned Paths 不重叠**是并行的物理前提；Shared Paths 由 Integration Owner 独占；Prohibited Paths 是子 agent 的"硬墙"
- **失败不传染**：单子任务失败不阻塞其他独立子任务；依赖失败子任务的下游必须转 `blocked`；Integration Owner 整合时跑 `full verify`，**任一退出非 0** 整批不得声明完成
- **chat 不替代文档**：可并行性判定、文件所有权、集成结果必须落字到 task packet 和 plan 末尾的 `## Session Handoff`，不靠对话历史传递

## 可并行判定（4 条件全满足才允许并行）

判断"两个子任务 A 和 B 能否并行"时，**4 个条件必须全部满足**；任一不满足则降级为串行。

| # | 条件 | 含义 | 判定方式 |
|---|---|---|---|
| 1 | **任务无顺序依赖** | A 不依赖 B 的产物，反之亦然；A、B 都不依赖对方未完成的 `Artifacts` | 检查 `task-packet.md` 的 `Depends On` 字段：A 的 `Depends On` 集合与 B 的 `Depends On` 集合**互不包含**；A 与 B 都不在对方的依赖路径上 |
| 2 | **Owned Paths 不重叠** | A 与 B 各自 `Owned Paths` 集合**交集为空**；任何文件不能被两个子 agent 同时声明所有权 | 集合差：A.Owned ∩ B.Owned = ∅ |
| 3 | **无同时修改共享配置** | A 与 B 都不在 `Shared Paths` 中出现，且 A 与 B 都不直接修改 CI / manifest / lockfile / 工作流脚本 | A.Shared ∩ B.Owned = ∅，B.Shared ∩ A.Owned = ∅，A.Shared ∩ B.Shared = ∅（共享文件**只能**由 Integration Owner 改） |
| 4 | **可独立验证** | A 完成后能跑 `Local Verify` 得到独立结论（不依赖 B 的产物）；B 同理 | 列出 `Local Verify` 命令并确认每条命令的输入文件**全部**位于 A.Owned 或其依赖产物的只读基线上 |

**降级规则**：

- 条件 1 不满足 → 串行（先完成被依赖任务再开始下游）
- 条件 2 不满足 → 把重叠文件**重新拆分**（按模块 / 区域 / 接口边界切分），或把整个合并到 Integration Owner
- 条件 3 不满足 → 把命中文件移到 `Shared Paths`，由 Integration Owner 串行处理
- 条件 4 不满足 → 串行或拆分到 Integration Owner 阶段

> **已取代**：本 runbook 早前没有显式列出 4 条件；该版本与 [task-packet.md](../templates/task-packet.md) 的 `Depends On` / `Owned Paths` / `Shared Paths` 等字段不构成完整判定链。**现行规则要求 4 条件全满足才允许并行**；任何"以 3 条件为充分条件"的旧表述自本 runbook 起不再适用。

## 8 字段 schema（task packet 批量子字段）

每个子任务的 task packet（按 [task-packet.md](../templates/task-packet.md)）必须包含以下 8 个**批量子字段**；任一缺失或为空视为该子任务**不**可进入并行调度。

| 字段 | 类型 | 含义 | 填写要求 |
|---|---|---|---|
| **Owner** | agent 名（如 `worker-A` / `planner-1`） | 负责本子任务的实施 agent；其在仓库内的全部写入**只能**落在 `Owned Paths` 之内 | 与 `session-handoff-protocol.md` 的 `Artifacts` 提交者一致；缺值视为未指派 |
| **Owned Paths** | 仓库相对路径集合（glob 或具体路径） | 本子任务**可以**修改的路径；其他子任务**不得**触碰 | 集合内每个路径必须存在或为新建路径；不允许指向 `docs/ai/`、`AGENTS.md`、`.github/`、CI manifest 等仓库级约定 |
| **Shared Paths** | 仓库相对路径集合 | 本子任务**间接依赖但不得直接落盘**的路径；任何修改必须由 Integration Owner 串行 | 子 agent 可在 `Local Verify` 读取 Shared Paths；**不得**用 `write` / `edit` 工具落字 |
| **Prohibited Paths** | 仓库相对路径集合 | 本子任务**明确禁止**触碰的路径（即使物理上未在 Owned / Shared 中） | 用于把"安全红线"显式化；子 agent 触碰任一路径即视为越界 |
| **Depends On** | packet id 列表 | 本子任务的前置 packet id 列表；前置未完成则本任务**不得开始** | id 必须是 [task-packet.md](../templates/task-packet.md) 顶部已声明的子任务 id；不允许依赖未声明的隐式 packet |
| **Local Verify** | 命令列表 | 本子任务完成后**必须**跑通的最小验证集合；每条命令必须能在不依赖其他子任务产物的环境下执行 | 与 [verification-baseline.md](../verification-baseline.md) 的 `minimal` / `l1` / `fast` 档位对齐；命令**不得**包含跨 packet 写操作 |
| **Integration Owner** | agent 名 | 集成阶段负责合并所有子任务产物、修改 Shared Paths、跑 `Integration Verify` 的 agent | 必须与子 agent **不同**；缺值视为集成阶段未指派，整批不得开始集成 |
| **Integration Verify** | 命令 | Integration Owner 在合并所有 Owned 产物并修改 Shared Paths 后跑的**最终**完整验证；通常是项目根 `verify` 入口 | 必须等于 `AGENTS.md` 顶部"用户项目元信息"段登记的 `full` 验证入口；缺值视为未声明集成门禁 |

> **模板归属**：以上 8 字段是 [task-packet.md](../templates/task-packet.md) 模板的一部分；本 runbook 不复制 schema 全文，只规定其在批量协作中的语义与门禁。下次实施批量任务时，直接复制 task-packet.md 并在指定位置填写 8 字段。
>
> **与 implementation-plan.md 的关系**：plan 模板 [implementation-plan.md](../templates/implementation-plan.md) **不必**新增 batch 子字段；plan 仍按 L2/L3 通用字段填写，批量协作的"8 字段"完全在 task packet 层声明（plan 引用 packet 即可）。仅当批量任务首次引入时，建议在 plan 顶部加一句"按 [batch-ai-execution-runbook.md](./batch-ai-execution-runbook.md) 拆分"。

## 冲突处理（Shared Paths 由 Integration Owner 独占）

并行实施期间，**任何 Shared Path 不得被子 agent 直接落盘**。

### 子 agent 的硬约束

- 子 agent 在 Owned Paths 之外**不得**调用 `write` / `edit` 等落盘工具
- 子 agent 如果发现"必须改 Shared Path 才能完成任务"，必须**立即停止**并把：
  - 期望修改的路径
  - 期望的 diff（before/after）
  - 修改理由
  提交到 plan 末尾的 `## Session Handoff.Decisions` 或单独 patch 说明文件，**由 Integration Owner 串行处理**
- 子 agent 在 `Local Verify` 阶段**可以**读取 Shared Paths，但**不得**把它作为输出

### Integration Owner 的独占权

- 集成阶段**只**由 Integration Owner 修改 Shared Paths；任何其他 agent 在集成阶段对 Shared Path 的写入均视为越界
- Integration Owner 在跑 `Integration Verify` 前必须**完整**收集所有子任务的 Owned 产物，并按子任务提交顺序合并；遗漏任一 Owned 产物即视为集成未完成
- Integration Owner 修改 Shared Path 时必须保留子 agent 提交的"期望 diff"作为决策依据；偏离必须有 `## Session Handoff.Decisions` 中的理由记录

### Prohibited Paths 的硬墙

- 子 agent 触碰 Prohibited Paths 任意一个 → 整批立即停止
- Integration Owner 也**不得**在 Prohibited Paths 中添加路径；Prohibited Paths 只在 task packet 阶段声明

## 失败隔离（单任务失败不污染整批）

并行调度必须把"单子任务失败"的影响**圈定**在最小范围。

### 单子任务失败的圈定

- **子任务失败 = 退出非 0 / `Local Verify` 任一条不通过 / 子 agent 主动声明 `Status: blocked`**
- **独立任务继续**：失败子任务不影响其他**无依赖**子任务继续实施
- **依赖任务转 blocked**：任何 `Depends On` 包含失败子任务 id 的下游子任务**必须**转 `Status: blocked`；Integration Owner **不得**合并 blocked 状态的子任务产物
- **失败原因落字**：失败子任务的 `## Session Handoff.Status` 必须明确写 `blocked`，并在 `Open Questions` 中说明阻塞点
- **不得静默重试**：子 agent 在未收到 `## Session Handoff.Decisions` 中的人工许可前，**不得**自行重试失败的子任务

### 整批失败的硬门禁

- **Integration Verify 退出非 0** → 整批**不得**声明完成
- **任一子任务处于 `blocked` 状态且未解决** → 整批**不得**声明完成
- **Shared Paths 未由 Integration Owner 独占修改** → 整批**不得**声明完成
- 整批完成的最小条件见 [completion-criteria.md](../completion-criteria.md) 的"批量集成条件"段；本 runbook 不重写

### 失败汇报格式

失败时在 plan 末尾的 `## Session Handoff` 中追加以下字段（沿用 [session-handoff-protocol.md](./session-handoff-protocol.md) 的 11 字段）：

```markdown
- Status: blocked
- Completed: <已完成子任务 id 列表及其状态>
- Artifacts: <成功子任务的产物路径；失败子任务无产物>
- Decisions: <失败处理策略：阻塞 / 重试 / 拆分的决策>
- Open Questions: <失败子任务的阻塞点>
- Next Allowed Actions: <人工允许后 Integration Owner 可以继续的动作>
- Prohibited Scope: <禁止在本轮重试中扩大范围>
```

## 完整示例（三任务纸面演练）

> **目标**：本节给出 3 个子任务的纸面演练：A、B 完全独立可并行，C 命中 Shared Path 必须由 Integration Owner 串行处理。三个任务在一次 L2 实施 session 内被拆分派发，最后由 Integration Owner 集成。

### 场景

仓库 `repo-X` 需要一次 L2 改动：

- A 子任务：新增一个查询 API（`src/api/query.ts` + `tests/api/query.test.ts`）
- B 子任务：新增一个 UI 列表组件（`src/components/QueryList.tsx` + `tests/components/QueryList.test.tsx`）
- C 子任务：把查询 API 接入到入口路由（修改 `src/router/index.ts` 注册新路由）

### 任务 1 阶段：拆分与可并行判定

| 任务 | Owned Paths | Shared Paths | Depends On | Local Verify | 与谁冲突 |
|---|---|---|---|---|---|
| A | `src/api/query.ts`、`tests/api/query.test.ts` | `src/router/index.ts` | — | `pnpm test tests/api/query.test.ts` | 与 C 在 `src/router/index.ts` 冲突 |
| B | `src/components/QueryList.tsx`、`tests/components/QueryList.test.tsx` | — | — | `pnpm test tests/components/QueryList.test.tsx` | 无冲突 |
| C | — | `src/router/index.ts`（仅声明，不落盘） | A | `pnpm typecheck` | 与 A 在 `src/router/index.ts` 冲突（必须交给 Integration Owner） |

**4 条件判定**：

- A vs B：条件 1 满足（无依赖）/ 条件 2 满足（Owned 不重叠：`api/query.ts` ∩ `components/QueryList.tsx` = ∅）/ 条件 3 满足（无 Shared 冲突）/ 条件 4 满足（独立 `pnpm test`）→ **可并行**
- A vs C：条件 1 不满足（C 依赖 A）→ **串行**：A 完成后才允许 C 开始子任务侧的 patch 提交；C 的 Shared Path 落盘由 Integration Owner 处理
- B vs C：条件 1 满足（无依赖）/ 条件 2 满足（Owned 不重叠）/ 条件 3 满足（C 不会读 B 的文件，B 也不写 router）/ 条件 4 满足（B 的 typecheck/test 独立可跑）→ **可并行**

**结论**：A 与 B 并行派发；C 的产物由 Integration Owner 在 A 完成后串行处理。

### 任务 2 阶段：并行实施

- worker-A 在 `src/api/query.ts` 实现查询 API，产出 `Local Verify` = `pnpm test tests/api/query.test.ts` 退出 0
- worker-B 在 `src/components/QueryList.tsx` 实现列表组件，产出 `Local Verify` = `pnpm test tests/components/QueryList.test.tsx` 退出 0
- worker-C（Shared Path 提交者）：**不**直接修改 `src/router/index.ts`；把期望 diff（路由注册片段）以 patch 形式提交到 plan 末尾 `## Session Handoff.Decisions`，标 `Status: ready`，`Artifacts: [plan patch]`
- 三者均填 [task-packet.md](../templates/task-packet.md) 的 8 字段：worker-A 写 A 的 packet，worker-B 写 B 的 packet，Integration Owner 写 C 的 packet（C 的 Owned Paths 为空，Shared Paths 含 `src/router/index.ts`）

### 任务 3 阶段：Integration Owner 串行集成

- Integration Owner 收集：A 产物（`src/api/query.ts`）+ B 产物（`src/components/QueryList.tsx`）+ C 的期望 diff（路由注册）
- Integration Owner 独占修改 Shared Path `src/router/index.ts`：按 C 的期望 diff 注册新路由
- Integration Owner 跑 `Integration Verify` = `pnpm verify`（项目根 `verify` 入口）→ 退出 0
- 整批可声明完成；plan 末尾 `## Session Handoff.Status` 写 `completed`，`Artifacts` 列所有改动的仓库相对路径

### 失败场景示例

- 若 worker-A 的 `Local Verify` 失败 → worker-A 在 plan 末尾写 `Status: blocked`，`Open Questions` 写明假设不成立
- worker-B **不受影响**继续推进（B 与 A 无 `Depends On`）
- worker-C 因 `Depends On: A` 转 `Status: blocked`；Integration Owner 不得合并 C 的 patch
- 整批**不得**声明完成；待 worker-A 修复 + Integration Owner 重跑 `Integration Verify` 后再统一收口

## 完成定义（批量任务）

批量任务除继承 [completion-criteria.md](../completion-criteria.md) 的"五项条件"外，还需满足：

1. **可并行 4 条件**已在 task packet 中显式标注（Owner / Owned Paths / Shared Paths / Prohibited Paths / Depends On / Local Verify / Integration Owner / Integration Verify 全部填写）
2. **每个子任务跑过 `Local Verify`** 且退出 0，结果在子任务自己的 `## 验证证据` 段落字
3. **Shared Paths 由 Integration Owner 独占修改**；子 agent 未直接落盘 Shared Path
4. **Integration Verify 退出 0**（`full` 验证入口）；未跑项必须显式标注
5. **任一子任务 `Status: blocked`** 未解决 → 整批不得声明完成
6. **失败隔离生效**：失败子任务不影响无依赖子任务的继续推进；依赖任务转 `Status: blocked` 并落字

完成定义的判定在 [completion-criteria.md](../completion-criteria.md) 的"批量集成条件"段给出权威措辞；本 runbook 不重写完成门禁。

## 关联

- 通用 L2 三 Session 纪律：[l2-multi-session-runbook.md](./l2-multi-session-runbook.md)
- Session Handoff Schema：[session-handoff-protocol.md](./session-handoff-protocol.md)
- 任务分级：[../task-levels.md](../task-levels.md)
- 验证基线：[../verification-baseline.md](../verification-baseline.md)
- 完成定义：[../completion-criteria.md](../completion-criteria.md)
- 分支与 worktree：[../branch-strategy.md](../branch-strategy.md)
- AI 角色边界：[../ai-role-boundaries.md](../ai-role-boundaries.md)
- task packet 模板：[../templates/task-packet.md](../templates/task-packet.md)
- 评审清单：[../checklists/review-checklist.md](../checklists/review-checklist.md)
