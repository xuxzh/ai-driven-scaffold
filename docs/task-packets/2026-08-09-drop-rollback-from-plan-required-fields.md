# 任务包：从 review-checklist 的 plan 必含字段删除"回滚"

> L1 task packet。按 [task-packet.md](../../template/docs/ai/templates/task-packet.md) 模板填写。
> 关联 review finding：[docs/reviews/2026-08-09-ai-reading-path-restructure-review.md](../reviews/2026-08-09-ai-reading-path-restructure-review.md) 的 O2 项。

## 目标

统一 review-checklist 与 implementation-plan 模板的不一致：模板无 `## 回滚` slot，checklist 不再强制 plan 必含回滚段。回滚信息隐含在 plan"每 Task 一个 commit"结构（回滚 = `git revert <commit>` 逐 Task 回退）。

## 级别

`L1`。理由：单文件单目标（review-checklist line 31）；触及仓库级规则文件（评审门禁字段定义）→ 非 L0；不跨文件行为 / 数据流 / 入口 → 非 L2。

## 锚点

- `template/docs/ai/checklists/review-checklist.md` line 31（plan 必含字段行）
- 对照：`template/docs/ai/templates/implementation-plan.md`（无 `## 回滚` slot，已 `rg` 确认）

## 假设

删"/ 回滚"后，review-checklist 与模板一致；line 57 的"风险·回滚"（PR/MR 描述字段）保留（与 plan 必含字段无关）；doctor + governance consistency 仍通过。

## 最小改动

删 review-checklist line 31 的" / 回滚"：

- 前：`文件清单 / 任务切片 / 步骤 / 命令 / 验证 / 回滚 / 顶部 > 基于 spec： 行`
- 后：`文件清单 / 任务切片 / 步骤 / 命令 / 验证 / 顶部 > 基于 spec： 行`

## 验证

- `bash template/scripts/scaffold-doctor.sh --template` → exit 0
- `python3 template/scripts/check-governance-consistency.py --root . --template` → exit 0
- `rg "回滚" template/docs/ai/checklists/review-checklist.md` → 仅 line 57（PR 描述字段）命中

## 非目标

- 不改 implementation-plan.md 模板骨架（不加 `## 回滚` slot）
- 不改 review-checklist line 57 的"风险·回滚"（PR/MR 描述字段保留）
- 不改其他评审检查项
- 不引入新机制

## 行为不变量

- 评审 session 仍按 review-checklist 评审；仅 plan 不再被强制要求显式回滚段
- PR/MR 描述仍要求"风险·回滚"（line 57 不变）

## 后续升级触发条件

- 若发现实施 session 因无强制回滚段而漏写高风险回滚路径 → 重新评估（回填强制要求或给模板加 `## 回滚` slot）

## 批量子字段

不适用（单 agent 串行，L1）。

## 验证证据（实施完成后必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `bash template/scripts/scaffold-doctor.sh --template` | 0 | Summary: 0 fail(s), 0 warning(s) | 删 line 31 回滚后 |
| `python3 template/scripts/check-governance-consistency.py --root . --template` | 0 | clean | |
| `python3 template/scripts/check-spec-and-plan-naming.py` | 0 | clean | |
| `rg "回滚" template/docs/ai/checklists/review-checklist.md` | 0 | 仅 line 57 命中 | line 31 回滚已删；line 57 PR 描述字段保留 |

未跑项：无（doctor / governance / naming 均跑，全退出码 0）
