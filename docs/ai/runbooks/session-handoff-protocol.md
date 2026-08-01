# Session Handoff Protocol

## 目的与适用范围

本协议定义 L2/L3 多 Session 之间的仓库内接力接口。下一 Session 必须只依赖仓库文件恢复任务状态，不依赖聊天历史；本文件是 schema、落点和停止门禁的唯一权威来源。

## 必填 Schema

每个 Handoff 必须填写以下 11 个字段；字段不得留空。枚举值仅在本协议允许的范围内使用。

| 字段 | 定义与填写要求 |
|---|---|
| **Task Level** | 当前任务等级：`L2` 或 `L3`，必须与任务分级及 plan 一致。 |
| **Current Phase** | 当前接力阶段：`planning`、`implementation` 或 `review`。 |
| **Status** | 当前状态：`ready`、`blocked` 或 `completed`；`blocked` 不得交给下一 Session 继续执行。 |
| **Completed** | 本阶段已经完成的具体工作；用可核对的条目描述。 |
| **Artifacts** | 本阶段产出的仓库文件、分支或报告路径；每个路径必须实际存在。 |
| **Decisions** | 已确定且对下一 Session 有约束力的决策及其依据。 |
| **Assumptions** | 执行所依赖、但尚未由系统验证的前提；没有时明确写“无”。 |
| **Open Questions** | 尚未解决、需要下一 Session 或人工回答的问题；没有时明确写“无”。 |
| **Verification** | 与当前阶段匹配的实际验证命令、退出码、关键输出和未跑项；规划阶段应明确“不要求 verify”。 |
| **Next Allowed Actions** | 下一 Session 允许执行的最小动作及前置条件。 |
| **Prohibited Scope** | 下一 Session 明确不得触及的文件、行为或任务范围。 |

## 物理落点与回填时机

- **L2 规划结束**：将 Handoff 写入对应 plan 文件末尾的 `## Session Handoff` 段。L3 的设计与计划阶段均应在各自交付物中保持可恢复的状态，并由最终 plan 作为实施入口。
- **实施结束**：更新同一 plan 的 Handoff；实际 verify 命令、退出码、关键输出和未跑项必须写入该 plan 的 `## 验证证据` 段。
- **评审结束**：将结果写入 plan 的 review 段，或写入独立 review report；review report 必须回链对应 plan，并在 plan 的 Handoff 中登记其路径。
- Handoff 必须位于交付物内、可从 `docs/ai/context-index.md` 和 L2 runbook 进入；聊天消息不能替代物理落点。

## 下一 Session 停止门禁

下一 Session 开始时必须先检查 Handoff。只要出现以下任一情况，必须停止，不得实施、推进或声明完成：

1. 11 个必填字段中任一缺失或为空；
2. `Status: blocked`；
3. `Artifacts` 中任一路径不存在；
4. `Verification` 与 `Current Phase` 不匹配（例如实施阶段缺实际 verify，或规划阶段声称已完成实施 verify）；
5. `Next Allowed Actions` 与 `Prohibited Scope` 无法明确界定下一步。

停止后只允许记录缺口并请求人工澄清或补齐上一个 Session 的交付物。

## Markdown Schema 模板

下次可直接复制以下块，并替换尖括号内容：

```md
## Session Handoff

- Task Level: <L2 | L3>
- Current Phase: <planning | implementation | review>
- Status: <ready | blocked | completed>
- Completed: <本阶段已完成事项；没有时写“无”>
- Artifacts: <仓库内路径列表；必须存在>
- Decisions: <已确定决策及依据；没有时写“无”>
- Assumptions: <执行前提；没有时写“无”>
- Open Questions: <待解决问题；没有时写“无”>
- Verification: <实际命令、退出码、关键输出、未跑项；规划阶段写“不要求 verify”>
- Next Allowed Actions: <下一 Session 允许执行的动作及前置条件>
- Prohibited Scope: <下一 Session 禁止触及的范围>
```
