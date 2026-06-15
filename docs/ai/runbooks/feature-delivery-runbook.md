# 业务功能交付运行手册（feature-specific）

> **本文档只描述"功能（feature）"工作流相对通用 L2+ 纪律的差异**。通用 4 session 纪律见 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)。

## 范围

本文档适用于"业务功能 + API/UI 原型"的 L2+ 任务。L0 / L1 任务不强制走 4 session，可直接做。

## 推荐切片顺序

第 2 会话（计划）的任务切片建议按以下顺序拆分：

1. 数据模型和字段定义
2. 适配层（service）和接口响应处理
3. 查询/缓存策略和变更失效
4. 列表、筛选、分页、排序
5. 表单、提交、反馈和确认交互
6. 文案（i18n / l10n）
7. 单元测试、页面测试或端到端测试
8. 最终验证和 AI review

## 实施 session 注意事项

- 视图/页面层不要消费后端原始响应
- 后端字段命名不适合前端时，在 service 或模型层做稳定映射
- 空字符串、undefined、null 的请求语义必须统一
- 分页、筛选、排序不要散落在视图里临时拼接
- 表单 schema 与验证规则独立于视图
- 不要把后端错误结构直接传给 UI

## 常见禁区（feature-specific）

除通用 L2+ 禁例外，feature 任务还应避免：

- 不要一上来让 AI 直接写完整页面
- 不要把请求逻辑直接写进入口或视图组件
- 不要把后端原始响应结构扩散到 UI
- 不要在端到端测试中依赖具体样式类名或脆弱 DOM 结构
- 不要把业务组件默认迁移到共享包
- 不要在没有明确批准时调整入口装配顺序、构建脚本、CI、依赖或仓库级规范
- 不要在没有验证结果时宣称完成

## 关联

- 通用 L2+ 4 session 纪律：[l2-multi-session-runbook.md](./l2-multi-session-runbook.md)
- 任务分级：[../task-levels.md](../task-levels.md)
- 完成定义：[../completion-criteria.md](../completion-criteria.md)
- 评审清单：[../checklists/review-checklist.md](../checklists/review-checklist.md)
- 模板：[feature-spec.md](../templates/feature-spec.md)、[implementation-plan.md](../templates/implementation-plan.md)
