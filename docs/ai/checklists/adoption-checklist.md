# 接入自检清单

> 本清单用于确认脚手架已经正确接入目标项目。它检查的是"治理脚手架是否可用"，不替代项目自身的 `verify`。

## 使用时机

- 新项目从模板创建后。
- 既有项目复制 `AGENTS.md`、`docs/ai/`、`docs/adr/` 后。
- 修改脚手架接入规则、CI 模板或项目元信息后。

## 人工检查

- [ ] `AGENTS.md` 存在，并且用户项目元信息已按项目实际情况填写。
- [ ] `AGENTS.md` 不再保留必填占位符：`<pm>`、`<app-dir>`、`<entry-file>`、`<shared-dir>`、`<test-dir>`。
- [ ] 项目 manifest 中存在 `verify` 入口，且该入口能覆盖当前项目的 lint、typecheck、test、build 需求。
- [ ] `docs/specs/` 和 `docs/plans/` 存在，用于承接 L2+ 任务交付物。
- [ ] 如启用 `.github/workflows/ci.yml` 或 `.gitlab-ci.yml`，其中的 `<...>` 占位符已经替换或删除。
- [ ] ADR-0002 / 0003 / 0004 / 0005 的状态与 `AGENTS.md` 中"硬约束依据"的表述一致。

## 脚本检查

从仓库根目录运行：

```bash
bash scripts/scaffold-doctor.sh
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
- doctor 通过后，L1+ 任务仍必须按 `verification-baseline.md` 运行项目 `verify`。
