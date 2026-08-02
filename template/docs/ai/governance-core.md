# AI 驱动开发治理基线

> 这是治理总览。具体的分级、完成定义、验证基线、分支策略、AI 边界、回写规则都已抽离为单点文件，请按链接查阅，避免此文档与单点定义漂移。

## 目标

为采用本脚手架的项目建立一套适用于个人或小团队开发优先场景的 AI 驱动开发治理方案，使 AI 参与研发后，交付过程仍然保持可理解、可验证、可回溯。

本治理采用平衡型策略，以交付稳定性为第一优先级，覆盖仓库内研发流程与轻量协作约束，包括：

- 任务分级与准入规则
- 功能、缺陷修复、重构、评审的标准工作流
- 验证基线与完成定义
- 文档沉淀与知识回流
- AI 角色边界与审批门
- 渐进式落地路线

## 非目标

本治理不追求以下目标：

- 不追求 AI 全面自治编码
- 不引入过重的组织级流程平台
- 不在第一版纳入完整 issue 流转与度量体系
- 不要求所有改动都强制走完整 spec 和 plan 链路
- 不把聊天记录本身视为长期知识资产

## 治理原则

本治理将采用本脚手架的项目定义为"**文档驱动、验证优先、AI 受控执行**"的工程仓库。AI 不是默认决策者，而是受流程约束的执行与分析工具。

首要目标是降低返工、误改和漏测风险，使 AI 参与开发后，仓库仍保持稳定边界和一致交付质量。治理采用平衡型策略：新功能、跨文件改动、数据流调整和中等以上重构必须先有 spec 和 plan 双份；局部小改动允许直接实施，但必须附带最小验证，并在必要时补回文档。

仓库内一切 AI 生成结果都默认需要通过测试、类型检查和人工判断共同确认，不能把模型输出本身当作完成依据。

## 单点文件索引

以下单点文件承载本治理的核心定义，所有其他文档（AGENTS.md、context-index、runbook、checklist）应链接到它们而不是各自复述：

- 任务分级 [task-levels.md](./task-levels.md)
- 完成定义 [completion-criteria.md](./completion-criteria.md)
- 验证基线 [verification-baseline.md](./verification-baseline.md)
- 分支与 worktree [branch-strategy.md](./branch-strategy.md)
- AI 角色边界 [ai-role-boundaries.md](./ai-role-boundaries.md)
- 文档回写规则 [doc-rewriting-rules.md](./doc-rewriting-rules.md)

## 硬约束依据（ADR）

本治理在 6 个单点文件之上，由 4 个 ADR 提供**硬约束依据**。这些 ADR 是治理基线收紧的来源，必须与单点文件同步阅读：

- [ADR-0002 将 verify 升级为 AI 必跑 + 必汇报](../adr/0002-verify-hard-gate.md)
- [ADR-0003 L2+ 任务强制多 session 串行](../adr/0003-multi-session-l2.md)
- [ADR-0004 L2 任务默认 spec + plan 都写](../adr/0004-l2-spec-and-plan.md)（修订 ADR-0001 L2 段）
- [ADR-0005 L3 任务 Pre-Implementation Approval Gate](../adr/0005-l3-approval-gate.md)

仓库级术语（如"锚点"、"准入门禁"、"验证层 vs 准入层"、"verify 报告"、"## 验证证据"等）定义在 `docs/CONTEXT.md`。

## 工作流入口

仓库内工作按四类分流入口，**所有工作流详细内容在 runbook / checklist，不再此文档复述**：

| 工作流 | 入口 runbook | 模板 |
|---|---|---|
| 功能 | [l2-multi-session-runbook.md](./runbooks/l2-multi-session-runbook.md) + [feature-delivery-runbook.md](./runbooks/feature-delivery-runbook.md) | [feature-spec.md](./templates/feature-spec.md)、[implementation-plan.md](./templates/implementation-plan.md) |
| 缺陷修复 | [l2-multi-session-runbook.md](./runbooks/l2-multi-session-runbook.md) + [bugfix-delivery-runbook.md](./runbooks/bugfix-delivery-runbook.md) | [bugfix-brief.md](./templates/bugfix-brief.md) |
| 重构 | [l2-multi-session-runbook.md](./runbooks/l2-multi-session-runbook.md) + [refactor-delivery-runbook.md](./runbooks/refactor-delivery-runbook.md) | [refactor-brief.md](./templates/refactor-brief.md) |
| 评审 | [checklists/review-checklist.md](./checklists/review-checklist.md) | — |

四类工作流共享同一原则：先确认任务级别，再决定是否需要 task packet 或 spec+plan 双份，然后进入最小可验证的实现闭环。

## 贯穿式要求

任何一轮 AI 实现之后，下一步优先是验证，而不是继续找更多优化点。AI 不得在没有验证结果的情况下宣称"已完成"或"应该没问题"。

## 渐进式落地路线

本治理采用渐进式落地，不一次性引入全部约束。

### 阶段 0：确立规则

先把本治理文档作为治理基线，明确：

- 哪些任务必须先写 task packet，哪些任务必须先写 spec 和 plan 双份
- 默认验证基线是什么
- 哪些情况必须审批
- 文档应沉淀到哪里

### 阶段 1：把文档变成默认入口

在日常开发中要求：

- 新功能和中等改动先走 spec 和 plan 双份
- 修复类任务先写问题定义和假设
- 改动完成后必须附验证结果

### 阶段 2：收紧高风险边界

开始对以下行为建立稳定习惯：

- 不跳过主链路验证
- 不在没有批准时推进基础设施变更
- 不把聊天结论代替文档
- 不让 AI 在一个任务中同时承担设计、实现和评审

### 阶段 3：再决定是否自动化

只有当阶段 0 到 2 已经稳定运转后，才评估是否引入：

- PR/MR 模板
- **CI 门禁**（注：CI 是**验证层**而非**准入层**——CI 模板在阶段 0 即可接入用于加固 verify 必跑纪律，详见 [ADR-0002](../adr/0002-verify-hard-gate.md)）
- issue 流转规范
- 度量指标

本治理不应在规则尚未跑顺前就引入过重的**准入**自动化约束（如强制 PR/MR 模板、强制 issue 模板），但**验证**类自动化（CI 跑 verify）不属此列。

## 成功标准

当以下条件稳定出现时，可认为本治理落地有效：

- 新功能和中等改动不再直接跳过 spec 或轻计划
- AI 结果开始稳定附带验证证据，而不是口头结论
- 高风险改动能够在执行前被识别并拦下审批
- 设计边界和经验性陷阱开始持续沉淀到文档而非聊天记录
- 单次任务的范围扩张和返工率明显下降
