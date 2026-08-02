# 接入自检清单

> 本清单用于确认脚手架已经正确接入目标项目。它检查的是"治理脚手架是否可用"，不替代项目自身的 `verify`。

## 使用时机

- 新项目从模板创建后。
- 既有项目复制 `AGENTS.md`、`docs/ai/`、`docs/adr/` 后。
- 修改脚手架接入规则、CI 模板或 Adoption Profile 后。

## 人工检查

- [ ] `AGENTS.md` 存在，并且 Adoption Profile（用户项目元信息）已按项目实际情况填写。
- [ ] `AGENTS.md` 不再保留必填占位符：`<pm>`、`<app-dir>`、`<entry-file>`、`<shared-dir>`、`<test-dir>`。
- [ ] 项目 manifest 中存在 `verify` 入口，且该入口能覆盖当前项目的 lint、typecheck、test、build 需求。
- [ ] `docs/specs/` 和 `docs/plans/` 存在，用于承接 L2+ 任务交付物。
- [ ] L2 任务**默认双文件交付**：spec（[feature-spec.md](../templates/feature-spec.md) 模板，含"非目标"与"验收"段）与 plan（[implementation-plan.md](../templates/implementation-plan.md) 模板，顶部必含精确 spec 路径引用）必须物理分离为两份独立文件。详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md) 与 [l2-multi-session-runbook.md](../runbooks/l2-multi-session-runbook.md)。
- [ ] L3 任务的 [ADR-0005](../../adr/0005-l3-approval-gate.md) Pre-Implementation Approval Gate 已生效：实施 session 启动前必须收用户"已批准"信号（spec / plan 双份路径 + 允许修改范围 + 禁止范围），且 `## 批准` 段顺序在 `## 验证证据` 段之前、批准不得跨任务复用。
- [ ] verify 落点统一：实施 session 必须跑项目根目录 `verify`，结果**同时**写入 spec 与 plan 双份末尾的 `## 验证证据` 段；规划 session 不跑 verify、仅接力交付物。
- [ ] 如启用 `.github/workflows/ci.yml` 或 `.gitlab-ci.yml`，其中的 `<...>` 占位符已经替换或删除。
- [ ] ADR-0002 / 0003 / 0004 / 0005 的状态与 `AGENTS.md` 中"硬约束依据"的表述一致。

## 脚本检查

从仓库根目录运行：

```bash
bash scripts/scaffold-doctor.sh
```

默认模式等价于：

```bash
bash scripts/scaffold-doctor.sh --adopted
```

维护本模板仓库时运行：

```bash
bash scripts/scaffold-doctor.sh --template
```

结果含义：

| 标记 | 含义 |
|---|---|
| `PASS` | 检查项满足预期 |
| `WARN` | 需要人工判断，但不阻塞脚本退出码 |
| `FAIL` | 接入缺失或明显不可用，脚本退出码为 `1` |

## 边界

- doctor 只读文件，不自动修复。
- doctor 只检查脚手架接入状态，不证明业务代码正确。
- `--template` 允许模板仓库保留 Adoption Profile 和 CI 模板占位符；`--adopted` 用于目标项目接入验收。
- doctor 通过后，L1+ 任务仍必须按 `verification-baseline.md` 运行项目 `verify`。
