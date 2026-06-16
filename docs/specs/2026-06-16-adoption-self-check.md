# Adoption Self-Check 设计

## 背景

本脚手架的核心定位是"可复制的 AI 协作治理文档包 + 轻量自检工具"。现有文档已经定义了任务分级、验证基线、分支策略、AI 角色边界、文档回写规则和 ADR 硬约束，但首次接入项目时仍有几类信息依赖人工记忆：

- `AGENTS.md` 中的项目元信息必须被替换，否则 AI 无法定位包管理器、入口、测试目录和完整验证入口。
- `docs/specs/` 与 `docs/plans/` 是 L2+ 任务交付物目录，但接入既有项目时需要人工创建。
- `verify` 是 L1+ 完成前的硬门禁，但脚手架目前只在文档中要求项目 manifest 定义它。
- CI 模板包含 `<...>` 占位符，如果未替换就直接启用，会导致 CI 配置不可用。
- ADR-0002 / 0003 / 0004 / 0005 被 `AGENTS.md` 作为硬约束引用，但 ADR 文件自身仍可能保留与现行规则冲突的状态表达。

这些问题不是治理规则缺失，而是"接入完成度"缺少一个统一检查入口。第一版应避免把脚手架变成完整 CLI，也不应引入具体技术栈绑定。

## 目标

提供一个轻量、只读的接入自检能力，让用户和 AI 能快速判断脚手架是否已经正确接入某个项目。

## 非目标

- 不自动修改用户项目文件。
- 不自动替换 `AGENTS.md` 或 CI 中的占位符。
- 不生成 manifest、依赖文件或 CI 配置。
- 不引入 Node / Python / Rust / Go 等运行时依赖。
- 不把 CI、hook、PR 模板做成强制准入门禁。
- 不覆盖具体业务项目的测试、构建或部署策略。

## 范围级别

- 建议任务级别：`L2`
- 理由：本次改动会新增脚手架目录能力、README 接入流程、维护清单和可执行脚本，属于跨文件的脚手架行为变化；但不改变现有治理硬约束，也不引入依赖或 CI 行为变化，因此不是 `L3`。

## 受影响边界

- 文档入口：`README.md` 的接入步骤需要加入自检说明。
- AI 治理清单：新增 adoption checklist，作为人工和 AI 的接入验收入口。
- 脚本边界：新增只读 `scripts/scaffold-doctor.sh`。
- 维护说明：`CONTRIBUTING.md` 需要补充脚手架自检维护要求。
- 长期决策：当前不新增 ADR；若后续把 doctor 从辅助脚本升级为强制门禁，再考虑 ADR。

## 建议方案

新增 `docs/ai/checklists/adoption-checklist.md`，定义接入完成的人工检查项；新增 `scripts/scaffold-doctor.sh`，用 POSIX shell 做只读检查并输出 `PASS` / `WARN` / `FAIL`。

doctor 第一版检查项：

1. `AGENTS.md` 是否存在。
2. `AGENTS.md` 是否仍包含必填占位符：`<pm>`、`<app-dir>`、`<entry-file>`、`<shared-dir>`、`<test-dir>`。
3. `docs/specs/` 与 `docs/plans/` 是否存在。
4. 项目 manifest 是否存在，并是否能识别 `verify` 入口。
5. `.github/workflows/ci.yml` 或 `.gitlab-ci.yml` 是否仍包含 `<...>` 占位符。
6. ADR-0002 / 0003 / 0004 / 0005 的状态是否仍为 `Proposed`，若它们在 `AGENTS.md` 中被称为硬约束，则报告为 `WARN`。

doctor 的退出码建议：

- `0`：没有 `FAIL`。
- `1`：存在至少一个 `FAIL`。

`WARN` 不阻塞退出码，用于提示接入质量问题或未来需要人工判断的问题。

## 备选方案

### 方案 A：只新增文档 checklist

优点是最轻，不引入脚本和跨平台顾虑。缺点是仍然依赖人工逐项检查，无法给 AI 一个稳定、可运行的接入状态信号。拒绝理由：对"AI 驱动脚手架"而言，缺少可执行检查会削弱落地效果。

### 方案 B：完整 init wizard / CLI

优点是首次接入体验最好，可以引导用户填写项目画像并生成配置。缺点是会引入运行时、安装方式、版本发布和跨平台兼容问题，偏离当前"语言无关治理包"定位。拒绝理由：第一版成本过高，且容易把治理脚手架变成工具链项目。

### 方案 C：CI 或 hook 强制接入自检

优点是约束更硬。缺点是与现有治理原则中"CI 是验证层而非准入层"的表述存在张力，也会让首次接入成本上升。拒绝理由：第一版应作为辅助检查，不作为强门禁。

## 验证计划

- 运行 `bash scripts/scaffold-doctor.sh`，确认在当前模板仓库中能报告预期的占位符和 ADR 状态提示。
- 运行 shell 语法检查：`bash -n scripts/scaffold-doctor.sh`。
- 运行文档占位符扫描，确认新增文档中的 `<...>` 均处于示例或检查目标语境。
- 检查新增 README / CONTRIBUTING 链接可达。

## 风险

- shell 脚本跨平台差异：第一版使用 POSIX shell 常见能力，避免依赖 GNU-only 参数。
- manifest 识别不完整：第一版只做常见 manifest 的保守识别，无法覆盖所有语言生态；未识别时报告 `WARN`，不直接失败。
- ADR 状态规范未完全定稿：第一版仅报告冲突风险，不自动改 ADR 状态。
- 用户误以为 doctor 通过等于项目质量通过：README 和 checklist 需要明确 doctor 只检查脚手架接入状态，不替代 `verify`。

## 需要更新的文档

- `README.md`：接入步骤中增加运行 doctor 的步骤，并说明只读性质。
- `CONTRIBUTING.md`：维护自检清单增加 doctor 脚本与 checklist 更新要求。
- `docs/ai/checklists/adoption-checklist.md`：新增接入清单。

## 批准（L3 任务必填，其他任务留空）

- 不适用，本任务按 `L2` 处理。

## 验证证据（实施 session 末尾必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |

未跑项：
