# AI 角色边界

> **这是单点定义文件**。所有 AI 协作场景（实施、评审、规划、文档维护）共用同一组角色边界。

## 设计原则

AI 是**受控执行者**，而不是仓库默认决策者。AI 可以承担分析、拆解、实现、验证和评审辅助职责，但**不拥有**默认的策略变更权和范围扩张权。

## AI 可承担的职责

- 基于现有规则起草 task packet、spec、plan
- 在明确锚点下实施局部改动
- 运行和汇报验证
- 补充测试和文档
- 按评审模式识别风险、回归和测试缺口
- 基于已有边界提供替代方案比较
- 按 [doc-rewriting-rules.md](./doc-rewriting-rules.md) 的回写规则更新文档

## AI 不可默认承担的职责

- 自行扩大任务范围（"顺手优化"）
- 自行改变仓库级默认约定（如包管理器、目录结构、入口装配顺序）
- 在无明确批准的情况下调整基础设施（CI / 部署 / 环境变量 / 鉴权）
- 将高风险任务降级为低风险任务
- 用"顺手重构"名义改动无关代码
- 在没有验证证据的情况下宣称完成
- 把聊天结论当作长期知识资产而不回写文档

## 必须显式审批的场景

以下情况必须由你显式确认后，AI 才能继续推进：

- 跨 package 或跨 workspace 改动
- 依赖升级或锁文件大幅变化
- 入口主链路或数据流边界调整
- Provider 顺序或应用壳层改动
- CI、部署、环境变量和安全相关变更
- 对 `AGENTS.md` 或其他仓库级规范文件的实质性修改
- 删除、重命名或迁移现有结构

AI 在遇到上述场景时，先给出变更意图、风险点和建议路径，再等待明确批准，而不是直接实施。

## 推荐角色模型

即便当前以个人工作流为主，也建议在使用 AI 时显式区分以下角色，以减少上下文漂移：

- **设计辅助者**：负责收敛需求、形成 spec
- **计划拆解者**：把 spec 转成可执行计划
- **实施者**：只按单一任务做代码改动
- **审查者**：只看风险、回归和测试缺口
- **文档维护者**：把稳定结论回写到仓库知识库

## 角色边界 = 会话边界（L2+ 强制）

按任务等级区分 session 数。L2 任务**必须**按"规划 / 实施 / 评审"三 Session 串行；L3 任务**必须**在 L2 之上叠加"设计 + 计划"双 Session（共四 Session）并加实施前明确批准（详见 [ADR-0003](../adr/0003-multi-session-l2.md) 与 [ADR-0005](../adr/0005-l3-approval-gate.md)）。

### L2 三 Session（规划 / 实施 / 评审）

| 角色 | Session | 交付物 |
|---|---|---|
| 设计辅助者 + 计划拆解者 | 规划 session | `docs/specs/<date>-<name>.md` + `docs/plans/<date>-<name>.md`（**始终是两份独立文件**） |
| 实施者 + 文档维护者 | 实施 session | 代码 + 测试 + `## 验证证据` 段 |
| 审查者 | 评审 session（**默认新开**） | review report（按 [review-checklist.md](./checklists/review-checklist.md) 结构） |

**规划 session 的内部步骤**：先写 spec → 用户明确确认 → 再写 plan；spec 与 plan 物理分离是硬门禁，不允许"快速通道"把两份文件合并成一份。

### L3 四 Session（设计 / 计划 / 实施 / 评审）

| 角色 | Session | 交付物 |
|---|---|---|
| 设计辅助者 | 设计 session | `docs/specs/<date>-<name>.md`（仅 spec） |
| 计划拆解者 | 计划 session | `docs/plans/<date>-<name>.md`（仅 plan） |
| 实施者 + 文档维护者 | 实施 session | 代码 + 测试 + `## 验证证据` 段 + `## 批准` 段；**必须先收用户"已批准"信号**（详见 [ADR-0005](../adr/0005-l3-approval-gate.md)） |
| 审查者 | 评审 session（**默认新开**） | review report（按 [review-checklist.md](./checklists/review-checklist.md) 结构） |

### 通用约束

- L2+ 任务**不得**由一个 session 串完全部角色——实施者自审的盲点（行为回归、边界破坏、验证缺失、测试缺口）会被同一上下文覆盖，治理失效。
- L0 / L1 任务可单 session 串完——多 session 是 L2+ 的入场费，不向下传递。
- 各 session 角色的边界如下：
  - **规划者**（L2）/ **设计 + 计划者**（L3）：**只产** spec 与 plan；**不**修改业务代码、**不**直接跑 `verify`、**不**起实施动作；不通过 spec/plan 形式隐式包含任何业务代码改动
  - **实施者**：**只读**已确认交付物（spec + plan 双份）；不允许在没有 spec/plan 就位的情况下实施；不允许"边写边补 spec/plan"
  - **评审者**：**不承担首轮实现**；默认新开 session；只读 `git diff`、spec、plan、`## 验证证据`（L3 还包括 `## 批准` 段），**不**预读实施 session 的中间对话

> **已取代**：本节早前版本要求 L2+ 任务一律按"设计 / 计划 / 实施 / 评审" 4 Session 串行，并允许"小 L2 快速通道"合并 spec/plan 物理分离。该版本已被 [ADR-0003](../adr/0003-multi-session-l2.md) 2026-08-01 修订取代；**现行规则为 L2 三 Session、L3 四 Session，spec 与 plan 始终物理分离**。

### 角色合并原则

5 个 AI 角色中，**判断被 ADR / 单点文件严格约束**的角色可与相邻 session 合并，不强制独立。当前实例：

- **设计辅助者 + 计划拆解者 = 1 session**（仅 L2 适用）
  - 合并依据：spec 与 plan 都是设计期交付物，输出相互依赖，物理分离已由 ADR-0004 的"spec + plan 双文件"硬门禁承担；不需要再用 session 边界强化
  - 兜底机制：spec 必须先经用户确认后再写 plan；评审 session 必查"spec 与 plan 是否物理分离 + spec 是否先于 plan"
  - L3 任务不享受此合并：L3 涉及 CI / 依赖 / 仓库级约定，spec 与 plan 的内容分工需要更强的会话切换支撑
- **实施者 + 文档维护者 = 1 session**
  - 合并依据：[doc-rewriting-rules.md](./doc-rewriting-rules.md) 的 4 条触发条件把"是否回写文档"约束到是/否
  - 兜底机制：评审 session 必查"是否有遗漏的文档回写"（[review-checklist.md](./checklists/review-checklist.md)）
  - 后续若新增被强约束的角色，可继续合并；新增原则写入 [CONTEXT.md](../CONTEXT.md) 的"角色边界 = 会话边界"段

## 关联

- 完成定义：[completion-criteria.md](./completion-criteria.md)
- 任务分级：[task-levels.md](./task-levels.md)
- 评审清单：[checklists/review-checklist.md](./checklists/review-checklist.md)
