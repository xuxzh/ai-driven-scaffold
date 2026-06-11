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
3. **必要验证已经执行**
   - 至少跑过与改动直接相关的最小验证
   - 主链路变化时补了端到端验证
   - 验证结果有命令输出可证
4. **没有新增与改动直接相关的错误**
   - 验证未引入新告警或失败用例
   - 任何新失败点已被明确处理或被显式说明
5. **触及长期约定时，文档已经同步更新**
   - 边界、默认做法、验证路径变化时回写 AGENTS.md / specs / plans / adr / runbook
   - 详见 [doc-rewriting-rules.md](./doc-rewriting-rules.md)

## 验证证据要求

AI 在汇报结果时**必须**说明：

- 跑了哪些检查
- 哪些通过
- 哪些未跑
- 未跑的原因

若环境限制导致无法执行某项验证，AI 必须明确说明缺口，不能把缺失验证包装成成功。

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
