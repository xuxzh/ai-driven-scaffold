# L2+ 多 session 串行工作流（通用）

> **本运行手册定义 L2+ 任务通用的 4 会话串行纪律**——所有 L2+ 任务类型（功能、缺陷修复、重构）共享。
>
> **任务类型特定差异** 参见：
> - 功能（feature）：[feature-delivery-runbook.md](./feature-delivery-runbook.md)
> - 缺陷修复：[bugfix-delivery-runbook.md](./bugfix-delivery-runbook.md)
> - 重构：[refactor-delivery-runbook.md](./refactor-delivery-runbook.md)

## 目的

本文档定义 L2+ 任务在仓库内如何按 4 个独立 session 串行完成需求分析、设计、计划、实施和评审。

**默认目标不是让 AI 在一个 session 内生成完整代码**，而是让 AI 在明确边界内受控执行，每 session 留下可回看的交付物与验证证据，下一 session 从仓库文档接力（详见 [ADR-0003](../../adr/0003-multi-session-l2.md)）。

## 适用范围

L2+ 任务。本文档定义通用纪律；任务类型特定内容由各 task-type runbook 给出。

L0 / L1 任务可单 session 串完——多 session 是 L2+ 的入场费，不向下传递。

## 总体原则

- **会话边界 = 角色边界**：4 个 session 串行，不允许单 session 串完全部 4 个角色
- **设计 session 先收敛需求**，再让后续 session 在边界内执行
- **每 session 结束前**输出"本 session 完成信号"+ 交付物路径，让下一 session 从仓库接力
- **用户可见行为必须有验证证据**（继承 [ADR-0002](../../adr/0002-verify-hard-gate.md)）
- **AI 汇报时必须说明**：实际运行了哪些命令、哪些通过、哪些未运行及原因

## 任务分级

L2+ 任务的适用情形详见 [task-levels.md](../task-levels.md) 与 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)。L2 走通用 4 session；L3 在 4 session 之上叠加 [ADR-0005](../../adr/0005-l3-approval-gate.md) 的 Pre-Implementation Approval Gate。

如果需求触及鉴权、权限模型、部署、CI、依赖升级、跨 workspace 重构或仓库级默认约定，应提升为 `L3`，由人工主导并在实施 session 启动前收用户明确批准。

## 4 会话串行总览

| Session | 角色 | 必读输入 | 必交付物 | 必跑 verify |
|---|---|---|---|---|
| **设计** | 设计辅助者 | AGENTS.md + context-index + task-levels + 接口/UI 文档 | `docs/specs/<date>-<name>.md` | 不要求 |
| **计划** | 计划拆解者 | 上一 session 的 spec | `docs/plans/<date>-<name>.md` | 不要求 |
| **实施** | 实施者 + 文档维护者 | spec + plan 双份 | 代码 + 测试 + `## 验证证据` 段 | **必须**跑 `verify` |
| **评审** | 审查者（**默认新开 session**） | 实施交付物 + 不读实施 session 中间对话 | review report（按 [review-checklist.md](../checklists/review-checklist.md)） | 含"测试盲区"清单 |

L3 任务在"实施 session 启动前"增加一道门：必须先收用户"已批准"信号，详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)。

---

## 第 1 会话：设计（设计辅助者）

**目标**：把需求转化为仓库内可执行的 spec。

**必读入口**：

- `AGENTS.md`
- `docs/ai/context-index.md`
- `docs/ai/task-levels.md`
- `docs/adr/0004-l2-spec-and-plan.md`（spec / plan 内容分工）
- 项目自身的接口/UI 规范（如有）

**必交付物**：`docs/specs/<date>-<name>.md`，按对应模板填写：

- 功能：[feature-spec.md](../templates/feature-spec.md)
- 缺陷修复：[bugfix-brief.md](../templates/bugfix-brief.md)
- 重构：[refactor-brief.md](../templates/refactor-brief.md)

**必含字段**（spec 必含）：

- 背景、目标、非目标
- 受影响边界（路由 / 数据流 / 状态 / 共享组件 / 工具链）
- 备选方案与拒绝理由
- 风险与未决问题
- 验证计划（**总体策略**，具体命令留给 plan）

**必输出信号**：本 session 末尾输出一段"设计 session 完成，交付物：`docs/specs/<date>-<name>.md`"。

**不允许**：

- 写代码或修改业务文件
- 写 plan（plan 是下一 session 的事）
- 写 verify 报告（验证由实施 session 跑）

**完成后人工检查**：

- 目标是否准确
- 非目标是否足够明确
- 是否存在 AI 自行扩大范围
- 接口字段和 UI 行为是否被正确理解
- 未决问题是否需要先问业务或后端

---

## 第 2 会话：计划（计划拆解者）

**目标**：把 spec 拆成多个可独立验证的实现切片，写入 plan。

**必读入口**：

- 上一 session 产出的 spec
- `docs/ai/templates/implementation-plan.md`（plan 模板）
- `docs/ai/verification-baseline.md`（每切片的 verify 命令应从这里推导）

**必交付物**：`docs/plans/<date>-<name>.md`，按 [implementation-plan.md](../templates/implementation-plan.md) 模板填写。

**plan 抬头必须**：

```markdown
> 基于 spec：[docs/specs/<date>-<name>.md](...)
```

否则视为与 spec 失联（详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)）。

**必含字段**（plan 必含）：

- 文件清单（新建 / 修改 / 测试）
- 任务切片（按可验证切片拆分）
- 每切片：步骤 / 命令 / 预期结果
- 验收标准
- 明确不做什么

**必输出信号**：本 session 末尾输出一段"计划 session 完成，交付物：`docs/plans/<date>-<name>.md`"。

**不允许**：

- 写代码（实施是下一 session 的事）
- 跳过 spec 直接写 plan
- 把 plan 写成 spec 的复制（plan 必须有可执行步骤）

---

## 第 3 会话：实施（实施者 + 文档维护者）

**目标**：按 plan 切片逐步实施，每切片完成即跑对应验证；实施 session 末尾跑 `verify` 并把结果写入 `## 验证证据` 段。

**L3 任务的前置条件**：必须先收用户"已批准"信号（"已批准" / "approved" / "proceed" / "go-ahead" / "确认执行" 任一字眼）并引用 spec/plan 路径。**缺信号时 AI 不得跑 `git add` / `git commit` / 直接 patch / 创建 MR / 直接 push**（详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)）。

**必读入口**：

- 上一 session 产出的 spec + plan 双份
- `docs/ai/branch-strategy.md`（分支 / worktree 选择）
- 项目根目录的 `verify` 命令

**必交付物**：

- 按 plan 切片实施的代码 + 测试
- spec 文件或 plan 文件末尾的 `## 验证证据` 段（详见下文"必跑 verify"）

**必跑 verify**（继承 [ADR-0002](../../adr/0002-verify-hard-gate.md)）：

- 实施 session 末尾**必须**跑项目根目录的 `verify` 入口
- 把命令的实际退出码与关键输出摘要写入 `## 验证证据` 段
- 未跑项必须显式标注原因
- 缺 verify 报告**不能**声明完成

`## 验证证据` 段格式示例：

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

**L3 任务追加要求**：在 `## 验证证据` 之前增加 `## 批准` 段：

```markdown
## 批准

- 批准时间：YYYY-MM-DD
- 批准来源：<issue-link> / <PR-link> / 会话消息引用
- 批准范围：与 spec 显式声明的范围一致
```

**必输出信号**：本 session 末尾输出"实施 session 完成，交付物：code at <branch> + 验证证据 at <spec-path>#验证证据"。

---

## 第 4 会话：评审（审查者，默认新开 session）

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

**必输出信号**：本 session 末尾输出"评审 session 完成，交付物：review report at <path>"。

**评审者不应**：

- 继续扩写功能
- 修改代码（修改代码是实施 session 的事）
- 给出空泛通过结论

---

## 快速通道（小 L2 例外）

若 L2 任务规模 < 半天，可在 spec 顶部加 `## 快速通道` 段并简述合并理由，**合并"设计 + 计划"为 1 session**（仍保留"实施 + 评审"分离）。**此例外不豁免 spec，只豁免 spec 与 plan 的物理分离**——快速通道 spec 必须同时含 spec 与 plan 的必含字段。

## 完成定义

L2+ 任务只有同时满足以下条件，才能称为完成（详见 [completion-criteria.md](../completion-criteria.md)）：

- 4 个 session 的交付物都在仓库内（spec、plan、代码、`## 验证证据`、review report）
- L3 任务有 `## 批准` 段
- 实施 session 跑过 `verify` 且结果已写入 `## 验证证据`
- review report 含"测试盲区"清单
- 触及长期约定时文档已同步更新
- 未执行的验证有明确原因和残余风险说明

## 任务类型特定差异

各任务类型（功能、缺陷修复、重构）有各自的推荐切片顺序、注意事项和禁区，详见对应的 runbook：

- 功能：[feature-delivery-runbook.md](./feature-delivery-runbook.md)
- 缺陷修复：[bugfix-delivery-runbook.md](./bugfix-delivery-runbook.md)
- 重构：[refactor-delivery-runbook.md](./refactor-delivery-runbook.md)

## 关联

- 治理基线：[../governance-core.md](../governance-core.md)
- 任务分级：[../task-levels.md](../task-levels.md)
- ADR：[../../adr/0003-multi-session-l2.md](../../adr/0003-multi-session-l2.md)
