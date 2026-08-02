# AI 治理自动守卫与验证分层实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development`（推荐）或 `executing-plans` 逐任务实施；脚本行为必须使用测试先行。

**Goal:** 将治理规则转化为可运行的链接检查、doctor 检查、worktree wrapper、验证档位和 CI 证据链。

**Architecture:** 通用脚本承担可跨项目执行的事实检查，Adoption Profile 提供项目命令映射，工具专属 hook 只作为可选 adapter。Doctor 聚合 structure、links、consistency、verify 四类结果；CI 调用相同本地入口，不复制检查逻辑。

**Tech Stack:** POSIX Bash、Python 3 标准库、Git、GitHub Actions、GitLab CI

## Global Constraints

- 前置条件：`2026-08-01-ai-governance-rule-convergence.md` 已实施并通过评审。
- 本计划属于 L3 变更，实施前必须获得明确批准。
- 不引入 pip/npm/第三方 shell 依赖。
- 所有检查器必须只读；除 worktree wrapper 外不得修改用户项目。
- CI 是验证层，不替代 L3 Pre-Implementation Approval Gate。
- 模板仓库与 adopted 项目必须使用同一脚本，通过模式参数区分。

---

## 文件职责与变更范围

- Create: `scripts/check-markdown-links.py` — 相对 Markdown 链接检查。
- Create: `scripts/tests/test_check_markdown_links.py` — 链接检查器单元测试。
- Create: `scripts/check-governance-consistency.py` — 关键治理规则一致性检查。
- Create: `scripts/tests/test_check_governance_consistency.py` — 一致性规则测试。
- Modify: `scripts/scaffold-doctor.sh` — 聚合结构、链接、一致性和 verify 检查。
- Create: `scripts/tests/scaffold-doctor-test.sh` — doctor fixture 集成测试。
- Create: `scripts/worktree-add.sh` — 通用 worktree 创建与文件传播 wrapper。
- Create: `scripts/hooks/rewrite-worktree-add.sh` — 可选 Claude Bash hook adapter。
- Create: `scripts/tests/worktree-add-test.sh` — 临时 Git 仓库中的 wrapper 测试。
- Create: `template/.worktreeinclude.example` — 忽略文件传播示例。
- Create: `template/.claude/settings.example.json` — 可选 hook 配置示例。
- Modify: `docs/ai/verification-baseline.md` — minimal/l1/fast/full 语义。
- Modify: `docs/adr/0002-verify-hard-gate.md` — 分层验证硬门禁。
- Modify: `AGENTS.md`, `template/AGENTS.md` — Adoption Profile 命令映射。
- Modify: `.github/workflows/ci.yml`, `.gitlab-ci.yml` — 调用统一检查入口。
- Modify: `README.md`, `CONTRIBUTING.md` — 接入和维护命令。

### Task 1：以测试驱动实现 Markdown 链接检查

**Produces:** `check-markdown-links.py [--root PATH] [--template]`，成功退出 0，真实断链退出 1。

- [ ] 创建 `scripts/tests/test_check_markdown_links.py`，使用 `tempfile.TemporaryDirectory` 覆盖：有效文件、有效目录、URL、纯锚点、真实断链、模板占位符。

关键断言：

```python
self.assertEqual(result.returncode, 0)
self.assertIn("broken.md:1", broken_result.stdout)
self.assertEqual(broken_result.returncode, 1)
```

- [ ] 运行失败测试：

```bash
python3 -m unittest scripts.tests.test_check_markdown_links -v
```

Expected: FAIL，因为 `scripts/check-markdown-links.py` 尚不存在。

- [ ] 实现检查器：解析 Markdown inline links；忽略 `http://`、`https://`、`mailto:`、`#anchor`；去除目标锚点和 URL 编码；以当前 Markdown 文件父目录解析相对路径；模板模式仅忽略明确的 `<...>` 路径占位符和 `...`。

- [ ] 运行单测和仓库检查：

```bash
python3 -m unittest scripts.tests.test_check_markdown_links -v
python3 scripts/check-markdown-links.py --root . --template
```

Expected: 所有测试 PASS；仓库检查退出 0。若发现真实断链，修复断链，不扩大忽略规则。

### Task 2：以测试驱动实现治理一致性检查

**Produces:** 可检测已知高风险矛盾的检查器，而不是通用自然语言解析器。

- [ ] 创建测试，fixture 至少覆盖：L0 同时允许和禁止 main、L2 同时定义三/四 Session、快速通道合并 spec/plan、缺少 L3 approval 文案。

- [ ] 运行测试确认失败：

```bash
python3 -m unittest scripts.tests.test_check_governance_consistency -v
```

- [ ] 实现最小规则集，只扫描 `AGENTS.md`、`template/AGENTS.md`、`docs/ai/task-levels.md` 和相关 ADR；每条失败输出规则 ID、文件和行号。

规则 ID 固定为：

```text
GOV001 contradictory-main-policy
GOV002 contradictory-l2-session-count
GOV003 merged-spec-plan-fast-path
GOV004 missing-l3-approval-gate
```

- [ ] 运行测试和真实仓库检查：

```bash
python3 -m unittest scripts.tests.test_check_governance_consistency -v
python3 scripts/check-governance-consistency.py --root . --template
```

Expected: 全部退出 0。

### Task 3：重构 doctor 为四类只读检查

**Interfaces:**
- Consumes: Task 1/2 两个 Python 检查器。
- Produces: `scaffold-doctor.sh --template|--adopted` 的稳定汇总格式。

- [ ] 先创建 `scripts/tests/scaffold-doctor-test.sh`，在临时目录测试：缺必需文件失败、断链失败、规则冲突失败、无 manifest 在 template 模式 WARN、adopted 模式缺 verify 失败。

- [ ] 运行测试确认至少一个新增场景失败：

```bash
bash scripts/tests/scaffold-doctor-test.sh
```

- [ ] 将 doctor 内部拆为函数：

```text
check_structure
check_links
check_consistency
check_verify_profile
print_summary
```

保持现有 `PASS/WARN/FAIL` 输出兼容；子检查器非零必须累计 FAIL。

- [ ] 运行：

```bash
bash -n scripts/scaffold-doctor.sh
bash scripts/tests/scaffold-doctor-test.sh
bash scripts/scaffold-doctor.sh --template
```

Expected: 测试全部 PASS；模板仓库 `0 fail(s)`。

### Task 4：定义并检查 Verification Profile

**Produces:** 项目可映射但语义固定的 `minimal/l1/fast/full` 验证档位。

- [ ] 更新 `docs/ai/verification-baseline.md`：L0=minimum；L1=受影响层；L2 无主链路/构建风险=fast，否则 full；L3=full + 人工专项确认。

- [ ] 在 `template/AGENTS.md` Adoption Profile 增加明确字段：

```text
最小验证入口 | <command>
L1 验证入口 | <command>
快速验证入口 | <command>
完整验证入口 | <command>
```

允许“不适用”，但必须附理由；full 必须覆盖 lint/typecheck/test/build 或项目声明的等价风险面。

- [ ] 扩展 doctor fixture：合法 Node manifest、合法非 Node 声明、`verify: echo ok`、缺 test、缺 build、仅 CI 无本地入口。

- [ ] 实现 verify profile 检查：优先读取 Adoption Profile；对可识别 manifest 验证入口存在；无法可靠解析命令组成时 WARN，不伪装成 PASS。

- [ ] 运行全部 doctor 测试：

```bash
bash scripts/tests/scaffold-doctor-test.sh
bash scripts/scaffold-doctor.sh --template
```

Expected: 空壳 verify 和缺失 adopted verify 为 FAIL；不可识别生态为带原因 WARN。

### Task 5：实现并测试 worktree wrapper

**Produces:** 无特定 AI 工具依赖的安全创建入口及可选 Claude adapter。

- [ ] 创建失败测试：拒绝 `.worktrees/` 外路径、拒绝非法分支前缀、接受合法路径、传播 `.worktreeinclude` 文件、缺失源文件只 WARN。

```bash
bash scripts/tests/worktree-add-test.sh
```

Expected: FAIL，因为 wrapper 尚不存在。

- [ ] 实现 `scripts/worktree-add.sh`：在调用真实 `git worktree add` 前完成路径和分支校验；白名单由文档单点定义并在脚本顶部同步注明来源；成功后复制 `.worktreeinclude` 中存在的文件。

- [ ] 实现 `scripts/hooks/rewrite-worktree-add.sh`：只改写可安全识别的独立 `git worktree add`；复合命令和 `git -C` 形式拒绝并提示 wrapper；其他 Bash 命令静默放行。

- [ ] 添加示例文件，不把 `.env` 或真实凭据写入仓库。

- [ ] 运行：

```bash
bash -n scripts/worktree-add.sh
bash -n scripts/hooks/rewrite-worktree-add.sh
bash scripts/tests/worktree-add-test.sh
```

Expected: 全部退出 0，临时 worktree 在测试清理阶段被移除。

### Task 6：CI 接入与最终验收

- [ ] 修改 GitHub/GitLab CI，使二者调用同一组命令：

```bash
bash -n scripts/scaffold-doctor.sh
bash scripts/scaffold-doctor.sh --template
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
bash scripts/tests/scaffold-doctor-test.sh
bash scripts/tests/worktree-add-test.sh
```

- [ ] 更新 README/CONTRIBUTING，说明 template/adopted 模式、Verification Profile 和可选 hook；禁止将 Claude hook描述为通用硬依赖。

- [ ] 运行完整本地验证：

```bash
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v
bash scripts/tests/scaffold-doctor-test.sh
bash scripts/tests/worktree-add-test.sh
bash scripts/scaffold-doctor.sh --template
git diff --check
```

Expected: 全部退出 0，doctor `0 fail(s)`。

- [ ] 请求独立评审，重点检查脚本可移植性、失败退出码、fixture 清理和 CI 重复逻辑。

- [ ] 用户确认后按逻辑分组提交，不自动提交：

```bash
git add scripts template/.worktreeinclude.example template/.claude/settings.example.json
git commit -m "feat(scaffold): add executable governance guards"
git add docs/ai docs/adr AGENTS.md template/AGENTS.md README.md CONTRIBUTING.md .github/workflows/ci.yml .gitlab-ci.yml
git commit -m "docs(ai): define layered verification profile"
```
