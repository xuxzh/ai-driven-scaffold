# AI 治理 v2 Dogfood 报告（2026-08）

> **快照说明**：本文为演练当时（2026-08）的仓库结构快照记录。文中引用的 `.superpowers/sdd/...`、`scripts/...` 等路径可能已在后续重构（见 `2026-08-02-template-restructure`）中调整；本文保留原样作为历史记录，不作为当前路径权威。

> 本文件按 [`docs/ai/dogfood/README.md`](./README.md) 规范汇总 Plan C Task 5 实施成果，作为 Plan C Task 5 计划要求的最终交付物。

## 任务清单

| 任务 | 等级 | 锚点 | 实际耗时 |
|---|---|---|---|
| README.md 链接文本修正 | L0 | `README.md` | 20 s |
| GOV005 ADR 索引一致性检查 | L1 | `scripts/check-governance-consistency.py` | 440 s 实施 + 57 s 评审修正 |
| spec-and-plan-naming 检查器 | L2 | `scripts/check-spec-and-plan-naming.py` + `docs/specs/`、`docs/plans/` 双份 | ≈ 30 min |

## 等级判定依据

- **L0**：单文件、不跨模块、不改变默认行为（`README.md` 链接文本，URL 不变）
- **L1**：单目标常规改动（GOV005 一个新规则，2-4 文件）
- **L2**：跨文件行为 + 新增 CLI（spec + plan 双份 + 主检查器 + 单元测试）

## 运行命令与退出码

### L0

```text
$ rg -n 'L2\+ 多 session' README.md
README.md:90
$ # 手工修正 → 不涉及脚本
$ git diff --check
exit=0
```

### L1

```text
$ python3 -m unittest scripts.tests.test_check_governance_consistency -v
Ran 13 tests in 0.31s — OK
$ python3 scripts/check-governance-consistency.py --root . --template
exit=0
```

### L2

```text
$ python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v
Ran 14 tests in 0.42s — OK
$ python3 scripts/check-spec-and-plan-naming.py --root . --template
exit=0
$ bash scripts/scaffold-doctor.sh --template
Summary: 0 fail(s), 0 warning(s)
```

## 失败 / 绕过

- L0：0
- L1：评审命中 docstring 未声明 GOV005 动态扫描范围；实施 session 已修正并复审通过（复跑 17 测 OK、`--template` exit 0）
- L2：评审命中"plan 步骤 1 fixtures 命名合法但被注释指为非法"；实施 session 修正 fixtures 命名（`aaa.md`/`bbb.md`），未改测试断言；记录在 `task-c5-l2-impl.md` "Plan deviation" 段

## 评估指标

| 指标 | 结果 |
|---|---|
| 分级一致性 | 100%（与 `task-levels.md` 矩阵一致） |
| worktree 摩擦 | 0（继承现有 worktree，未新建） |
| handoff 恢复成功率 | 3/3（每任务可从仓库 + 报告/任务包恢复） |
| verify 耗时 | 单任务 < 2 s |
| 规则歧义 | 5 项（详见改进建议） |
| 自动守卫命中 | 0 命中；1 项由独立评审人工捕获（详见改进建议） |

## 改进建议（不自动成为硬门禁）

1. task-packet 8 字段对单 agent 串行 L1 任务冗余；建议 task-packet.md 顶部加"非批量子任务可折叠 Owner/Shared/Integration Owner 字段"说明
2. spec 文本与机制不对齐应在 spec 末尾显式登记（如 L1 docstring 范围说明）
3. L2 规划/批准时序歧义建议补 l2 runbook 段（"规划 Session 输出 plan + 收 Handoff 后，批准在前置位"）
4. `bash -n` 不适用于 Python 文件；CI lint-python job 应改用 `python3 -m py_compile`
5. `.superpowers/sdd/task-c5-l0-review.md` 与 `task-c5-l1-review.md` 缺失；建议下次 dogfood 全量保存所有 review 记录

## 备注

- 工作目录：`.worktrees/opt-ai-governance-v2-plans`，分支 `opt-ai-governance-v2-plans`
- 未触动 Plan A/B/C 已 approved 内容（除 Task 5 显式范围内新增）
- 未引入第三方依赖
- 报告只提建议，不自动成为硬门禁；任何采纳须另开 L1 spec/plan 任务