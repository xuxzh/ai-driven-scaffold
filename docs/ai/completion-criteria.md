# 完成定义

> **这是单点定义文件**。所有任务类型（功能、缺陷、重构、评审）共用同一组完成条件。

## 五项条件

一个任务只有**同时**满足以下条件，才能被视为完成：

1. **目标范围没有无控制扩张**
   - 改动未越过声明的非目标
   - 没有"顺手优化"无关代码
2. **改动与任务级别匹配**
   - `L0`/`L1` 没有被不当扩大为 `L2`/`L3`
   - `L2`/`L3` 走完了 spec/plan 准入流程
   - `L2` 任务按"规划 / 实施 / 评审" 3 个 session 串行完成（详见 [ADR-0003](./../adr/0003-multi-session-l2.md)）
   - `L3` 任务在 L2 之上叠加"设计 + 计划"双 Session（共四 Session），并在实施 session 启动前收用户明确批准信号（详见 [ADR-0005](./../adr/0005-l3-approval-gate.md)）
   - **接力完整性**：L2/L3 的 Session Handoff 11 个必填字段全部填写，且 `Artifacts` 中列出的路径均存在（详见 [Session Handoff Protocol](./runbooks/session-handoff-protocol.md)）
3. **必要验证已经执行**
   - L1+ 任务在汇报"完成"之前**必须**运行项目根目录的 `verify` 入口（详见 [ADR-0002](./../adr/0002-verify-hard-gate.md)）
   - L0 任务至少跑过与改动直接相关的最小验证
   - 主链路变化时补了端到端验证
   - 验证结果以 **verify 报告**形式落字（命令 + 实际退出码 + 关键输出摘要）
4. **没有新增与改动直接相关的错误**
   - 验证未引入新告警或失败用例
   - 任何新失败点已被明确处理或被显式说明
5. **触及长期约定时，文档已经同步更新**
   - 边界、默认做法、验证路径变化时回写 AGENTS.md / specs / plans / adr / runbook
   - 详见 [doc-rewriting-rules.md](./doc-rewriting-rules.md)

## 批量集成条件（L2+ 批量多 agent 协作时适用）

L2+ 任务在走完"五项条件"之上，若实施阶段由多个 worker agent 按 [batch-ai-execution-runbook.md](./runbooks/batch-ai-execution-runbook.md) 并行落地，整批**只有同时**满足以下条件才视为完成：

1. **可并行 4 条件已落字**：所有子任务的 [task-packet.md](./templates/task-packet.md) 8 字段（`Owner` / `Owned Paths` / `Shared Paths` / `Prohibited Paths` / `Depends On` / `Local Verify` / `Integration Owner` / `Integration Verify`）全部填写；可并行判定（无顺序依赖 / Owned Paths 不重叠 / 无同时修改共享配置 / 可独立验证）已在 task packet 中显式标注
2. **每个子任务跑过 `Local Verify`** 且退出 0，结果在子任务自己的 `## 验证证据` 段落字；未跑项与原因独立列出
3. **Shared Paths 由 Integration Owner 独占修改**：子 agent 未直接落盘 Shared Path；Shared Path 的修改必须由 Integration Owner 在集成阶段串行完成，并在 plan 末尾 `## Session Handoff` 中登记
4. **Integration Verify 退出 0**：Integration Owner 在合并所有 Owned 产物并修改 Shared Paths 后跑 `Integration Verify`（通常等于 `AGENTS.md` 顶部"用户项目元信息"段登记的 `full` 验证入口），且退出 0
5. **无未解决的 blocked 子任务**：任何 `Status: blocked` 的子任务必须在 `## Session Handoff.Open Questions` 中说明阻塞点，整批**不得**在仍有 blocked 子任务时声明完成
6. **失败隔离生效**：失败子任务不影响无依赖子任务继续推进；依赖任务转 `Status: blocked` 并落字；不得静默重试失败子任务

> 任何一条不满足 → 整批**不得**声明完成；Integration Owner 必须先把缺口补齐（修复失败子任务 / 重跑 `Integration Verify` / 修正 Shared Path 落盘责任）再统一收口。
>
> 详细纪律与纸面演练见 [batch-ai-execution-runbook.md](./runbooks/batch-ai-execution-runbook.md)；本段是完成门禁的唯一权威措辞，runbook 不重写。

## 验证证据要求

AI 在汇报结果时**必须**说明：

- 跑了哪些检查
- 哪些通过
- 哪些未跑
- 哪些是 `verify` 命令本身跑出的项
- 未跑的原因

若环境限制导致无法执行某项验证，AI 必须明确说明缺口，**不允许把缺失验证包装成成功**。L1+ 任务的"未跑项"必须在 verify 报告或会话汇报中显式标注，未标注视为"已跑但未报告"，按未跑处理。

## 与"任务完成"的关系

完成 ≠ AI 给出 patch。完成 = 变更已经通过与其风险等级相匹配的验证（详见 [verification-baseline.md](./verification-baseline.md)）并满足上述五项条件。

## 反例（不应算"完成"）

- 写出 patch 但没跑任何命令
- 跑了测试但跳过 lint/typecheck
- 改了边界但没回写文档
- 失败用例被注释掉而不是修复
- 在汇报中只写"应该没问题"而无命令输出

## 关联

- 验证基线：[verification-baseline.md](./verification-baseline.md)
- 任务分级：[task-levels.md](./task-levels.md)
- 评审清单：[checklists/review-checklist.md](./checklists/review-checklist.md)
