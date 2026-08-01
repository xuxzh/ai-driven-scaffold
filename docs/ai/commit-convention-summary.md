# Commit Convention · 快速摘要

> 本文仅为快速摘要；如有冲突，以链接的权威规范和 Accepted ADR 为准。

## 格式

`<type>(<scope>): <subject>` —— scope 可省略；subject 中文 / 英文均可，≤ 72 字符，祈使语气，不写句号。

## Type 白名单（11 类）

`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `build` / `ci` / `chore` / `revert`

## Breaking Change

`type(scope)!: <subject>` 或 footer `BREAKING CHANGE: <说明>`；两者必须一致。

## 提交边界（推荐切片）

spec / plan / implementation / review follow-up 分提交；不得混入无关修改；L2+ 必带 `Refs:` 到 spec + plan。

## AI 行为硬约束

1. 默认**不自动 commit**（用户明确要求才提交）
2. 不得**跳过 hooks**（`--no-verify` 须用户明确要求）
3. 不得 **amend** 未授权提交
4. 不得 **force-push**（共享分支强推须用户二次确认）
5. 不得擅自改 `user.name` / `user.email` 构造提交者身份

## PR / MR 必含字段

目标 / 范围 / 非目标 / 验证证据 / 风险·回滚；L2+ 必带关联 spec + plan。

## 权威来源

- 完整规范：[commit-convention.md](./commit-convention.md)
- 评审清单：[checklists/review-checklist.md](./checklists/review-checklist.md)
- ADR：[../adr/0002-verify-hard-gate.md](../adr/0002-verify-hard-gate.md)