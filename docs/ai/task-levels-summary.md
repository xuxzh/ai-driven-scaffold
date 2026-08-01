# L0 / L1 / L2 / L3 任务分级 · 快速摘要

> 本文仅为快速摘要；如有冲突，以链接的权威规范和 Accepted ADR 为准。

## 判定三问

按顺序回答；任一为"是"就向更高等级提升，AI 不得自行降级：

1. 改动是否改变用户可见行为？
2. 改动是否跨越已有边界（共享 utility / 入口装配 / 仓库级规则）？
3. 改动是否触及基础设施或仓库级约定（CI / 依赖 / 安全 / 鉴权）？

## 等级决策表

| 级别 | 典型场景 | 必备交付物 | 分支 / worktree |
|---|---|---|---|
| `L0` | 单文件内文案 / 注释 / 拼写 / 局部样式 / 已存测试 1 处断言；非共享文件内部实现重构（外部行为不变） | 无 packet / spec / plan；至少 1 个与改动直接相关的最小验证 | 任务分支必走；worktree 可选 |
| `L1` | 2–4 个文件内新增展示块 / 派生交互 / 已有入口补测试 / 数据访问层新增 1 个 service | task packet（目标 / 锚点 / 假设 / 最小验证 / 非目标） | 任务分支 + 独立 worktree |
| `L2` | 跨文件行为 / 跨目录 / 入口流转 / 数据流 / 状态边界 / 端到端预期 / 公共组件行为变化 | spec + plan 双份（始终物理分离），先 spec → 用户确认 → 再 plan | 任务分支 + 独立 worktree |
| `L3` | CI 变更 / 依赖升级 / 部署策略 / 跨 workspace 重构 / 全局脚手架 / 安全 / 鉴权 / 仓库级规范大幅改动 | L2 条件 + 实施 session 启动前**明确批准**信号（必须引用 spec/plan 路径） | 任务分支 + 独立 worktree |

## Session 编排（引用 ADR-0003）

- `L0` / `L1`：单 session。
- `L2`：3 个 session 串行（规划 / 实施 / 评审）；评审 session 默认新开。
- `L3`：4 个 session 串行（设计 / 计划 / 实施 / 评审）；实施前额外收"已批准"信号。

## 升级条件（何时不能停在 L0）

任何一条触发即升级：

- 改动跨 ≥ 2 个文件
- 触及共享边界（应用壳层 / 入口装配 / 根脚本 / 仓库级规则 / shared utility）
- 修改 props / 默认行为 / 公共类型签名
- 跨模块 / 进程 / 调用方产生预期变化
- 失败影响范围可能跨模块或跨工作流

## 降级禁止

- 用户明确指定 `L2` / `L3` 时 AI 不得降级
- 分级有争议 → 按更高风险处理
- L3 不得被当作普通 L2 直接执行

## 验证档位（验证强度）

- L0：最小验证（与改动直接相关的最窄检查）
- L1：受影响层验证（相关测试 + 局部 lint / typecheck）
- L2：覆盖静态 + 类型 + 受影响功能测试；主链路变化时补 E2E
- L3：完整基线 + 人工确认验证范围

## 权威来源

- 任务分级：[task-levels.md](./task-levels.md)
- 分支与 worktree：[branch-strategy.md](./branch-strategy.md)
- 验证基线：[verification-baseline.md](./verification-baseline.md)
- 完成定义：[completion-criteria.md](./completion-criteria.md)
- ADR：[../adr/0003-multi-session-l2.md](../adr/0003-multi-session-l2.md) / [../adr/0004-l2-spec-and-plan.md](../adr/0004-l2-spec-and-plan.md) / [../adr/0005-l3-approval-gate.md](../adr/0005-l3-approval-gate.md)
