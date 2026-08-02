# 任务包模板

> **L2+ 批量协作时**（把一次实施拆给多个 worker agent 并行落地），本模板的"8 个批量子字段"（`Owner` / `Owned Paths` / `Shared Paths` / `Prohibited Paths` / `Depends On` / `Local Verify` / `Integration Owner` / `Integration Verify`）为**必填**；可并行判定、文件所有权、共享文件独占、失败隔离的完整纪律见 [`docs/ai/runbooks/batch-ai-execution-runbook.md`](../runbooks/batch-ai-execution-runbook.md)。L0 / L1 任务这 8 个字段可标注"不适用（单 agent 串行）"。

## 目标

- 一个具体结果

## 级别

- 默认按 `L1` 处理；如果不是，说明为什么需要升级

## 锚点

- 主要文件或符号

## 假设

- 关于目标行为的一个局部、可证伪假设

## 最小改动

- 用来验证该假设的最小可行改动

## 验证

- 精确命令
- 预期结果

## 非目标

- 哪些内容必须保持在范围外

## 行为不变量（重构模式必填，其他任务可选）

- 哪些行为在改动后**必须保持不变**
- 用什么命令 / 断言来证明"行为未变"

## 后续升级触发条件

- 什么结果会触发升级到 spec 或完整实施计划

## 批量子字段（L2+ 批量协作时必填；其他任务写"不适用"并说明）

> 字段语义、填写要求与门禁见 [`batch-ai-execution-runbook.md`](../runbooks/batch-ai-execution-runbook.md) 的"8 字段 schema"段。本模板仅占位，不复制完整 schema。

- Owner: <agent 名；缺值视为未指派>
- Owned Paths: <本任务可修改的仓库相对路径集合>
- Shared Paths: <本任务间接依赖但不得直接落盘的路径；修改由 Integration Owner 独占>
- Prohibited Paths: <本任务明确禁止触碰的路径>
- Depends On: <前置 packet id 列表；前置未完成本任务不得开始>
- Local Verify: <本任务完成后必跑通的最小验证命令列表>
- Integration Owner: <集成阶段负责合并与 `Integration Verify` 的 agent>
- Integration Verify: <集成阶段跑的最终完整验证命令；通常等于项目根 `verify` 入口>

## 验证证据（实施完成后必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |

未跑项：
