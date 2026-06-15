# ADR-0001 使用任务分级治理 AI 改动风险

日期：2026-05-25

## 状态

Accepted（部分被 [ADR-0004](0004-l2-spec-and-plan.md) 修订）

## 修订记录

- **2026-06-15**：[ADR-0004](0004-l2-spec-and-plan.md) 通过；本 ADR 决策段中 `L2` 行的"或"被修订为"和"。本 ADR 的 L0 / L1 / L3 行不受影响。详见 [ADR-0004](0004-l2-spec-and-plan.md)。

## 背景

仓库目标是支持 AI 参与日常开发，同时保持改动可理解、可验证、可回溯。没有任务分级时，AI 容易把局部问题扩大成跨边界重构，也容易在缺少验证证据时宣称完成。

## 决策

仓库采用 `L0`、`L1`、`L2`、`L3` 四级任务治理模型：

- `L0`：单文件、不跨模块的轻量改动，可直接执行，但必须有最小验证。
- `L1`：单一目标的常规改动，先明确目标、锚点、假设、验证和非目标。
- `L2`：跨文件行为、路由、数据流、共享边界等中等风险改动，默认必须先有正式 spec 和 plan **双份**（详见 [ADR-0004](0004-l2-spec-and-plan.md)）。
- `L3`：依赖、CI、部署、安全、跨 workspace 重构等高风险改动，必须先有正式 spec 和 plan 双份，并由人工主导；实施 session 启动前必须收用户明确批准（详见 [ADR-0005](0005-l3-approval-gate.md)）。

任何代码改动前，AI 必须先说明当前变更级别。用户明确指定 `L2` 或 `L3` 时，AI 无权自行把任务降级；如分级存在争议，默认按更高风险级别处理。

正式 spec 和 plan 统一位于 `docs/specs/`、`docs/plans/`。聊天计划、临时 TODO、`update_plan` 输出不算正式文档；L2+ 任务必须两者都写（spec 必含设计决策与边界，plan 必含可执行切片与每切片命令），plan 抬头必须引用 spec 路径。`L3` 实施 session 启动前必须收用户明确批准信号，AI 不得自行推进实现。

## 后果

- 正向影响：AI 执行前先明确范围和验证，减少误改、漏测和无控制扩张。
- 约束或成本：中等以上改动会增加文档前置成本；L2 任务成本由 1 份文档升到 2 份。
- 后续触发条件：如果仓库引入完整 issue 流程或自动化任务系统，需要把分级模型映射到对应工作流。

## 关联

- 基线文档：[../ai/task-levels.md](../ai/task-levels.md)
- Runbook：[../ai/runbooks/development-runbook.md](../ai/runbooks/development-runbook.md)
- 修订本 ADR 的 ADR：[0004-l2-spec-and-plan.md](0004-l2-spec-and-plan.md)
- 引用本 ADR 的 ADR：[0002-verify-hard-gate.md](0002-verify-hard-gate.md)、[0003-multi-session-l2.md](0003-multi-session-l2.md)、[0005-l3-approval-gate.md](0005-l3-approval-gate.md)
