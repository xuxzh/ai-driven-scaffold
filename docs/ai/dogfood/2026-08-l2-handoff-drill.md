# L2 接力纸面演练（2026-08）

> 本文件为 Task 6 指定的"模拟一次 L2 接力"演练，**纸面演练**——不触发真实 agent / 不写实现代码 / 不修改任何规范文件。所有"会话"边界与"交付物"行为均按 [`docs/ai/runbooks/session-handoff-protocol.md`](../runbooks/session-handoff-protocol.md) 与 [`docs/ai/runbooks/l2-multi-session-runbook.md`](../runbooks/l2-multi-session-runbook.md) 的现有纪律还原。
>
> 演练背景：父计划 `docs/plans/2026-08-01-ai-session-batch-and-dogfood.md` Task 6 第 1 段。本演练**不**新增规则、不修改 ADR；只验证"新 Session 仅凭仓库文件即可恢复任务并执行"是否成立。

---

## 0. 演练主题

**演练名**：L2 接力恢复（handoff recovery drill）。

**目标**：在零对话历史的前提下，证明：

1. 规划 Session 仅产出 spec + plan 双份 + Handoff，未触发任何代码层变更；交接出口信号清晰。
2. 实施 Session **仅读取仓库文件**（无聊天上下文）即可恢复任务，按 plan 切片执行并完整跑 `verify`，把结果写回 spec 与 plan 双份的 `## 验证证据` 段。
3. 评审 Session **仅**消费 `git diff` + spec + plan + Handoff + `## 验证证据` 段，无需读到实施 Session 中间对话也能形成完整审查结论。

**演练锚点**：复用 `docs/specs/2026-08-02-spec-and-plan-naming-check.md` + `docs/plans/2026-08-02-spec-and-plan-naming-check.md` 作为已存在的 spec/plan 样本（不是本演练新写），用于模拟"实施 Session 从仓库恢复"。这避免了本演练去写新规则——只检验"接力"本身。

**演练边界**：

- 不修改任何仓库文件（演练产物为本文件 + 第 4 段"评审结论"段，按照"已存在样本"叙述即可）。
- 不新增 / 修改 / 撤销任何 ADR、规则、模板或运行手册。
- 纸面演练的"实施 Session"以"如果实际执行会跑这些命令"列出；不真跑 `git commit` / `git push` / 修改源文件。
- 演练报告只作为论文证据，不进入 `docs/adr/` 与 `docs/ai/runbooks/` 任何权威文件。

---

## 1. 规划 Session 出口信号

**角色**：规划 Session（设计辅助者 + 计划拆解者）。
**走读纪律**：[`l2-multi-session-runbook.md`](../runbooks/l2-multi-session-runbook.md) 第 1 Session 段 + [`session-handoff-protocol.md`](../runbooks/session-handoff-protocol.md) 11 字段 schema。

### 1.1 必读入口

下钻到仓库内具体文件：

| 入口 | 路径 |
|---|---|
| 仓库级 AI 治理入口 | `AGENTS.md` |
| 上下文索引 | `docs/ai/context-index.md` |
| 任务分级矩阵 | `docs/ai/task-levels.md` |
| spec / plan 双份分工 | `docs/adr/0004-l2-spec-and-plan.md` |
| 命名规范 | `docs/ai/spec-and-plan-naming.md` |
| 提交规范 | `docs/ai/commit-convention.md` |
| 分支与 worktree | `docs/ai/branch-strategy.md` |
| L2 通用纪律 | `docs/ai/runbooks/l2-multi-session-runbook.md` |
| Session Handoff schema | `docs/ai/runbooks/session-handoff-protocol.md` |
| 完成定义 | `docs/ai/completion-criteria.md` |
| 验证基线 | `docs/ai/verification-baseline.md` |

### 1.2 必交付物（仅 spec + plan + Handoff，不写代码）

- `docs/specs/2026-08-02-spec-and-plan-naming-check.md`：spec 一份；按 [`feature-spec.md`](../templates/feature-spec.md) 填写，含 `## 元信息` / `## 背景` / `## 目标` / `## 行为` / `## 非目标` / `## 验收` / `## 范围级别` / `## 受影响边界` / `## 建议方案` / `## 备选方案` / `## 验证计划` / `## 风险` / `## 需要更新的文档` / `## Session Handoff`。
- `docs/plans/2026-08-02-spec-and-plan-naming-check.md`：plan 一份；按 [`implementation-plan.md`](../templates/implementation-plan.md) 填写，**物理独立**于 spec（详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)）；抬头必含 `> 基于 spec：[...](...)` 行。
- Handoff：在 plan 末尾 `## Session Handoff` 段按 11 字段 schema 填写（见 §1.4）。

### 1.3 规划 Session 末端的"自检清单"（实施 Session 接管前必查）

- [ ] spec 与 plan **物理分离**为两份独立文件（未合并）。
- [ ] spec 已先经用户确认（"已确认 spec" / "approved" / "proceed" 等任一字眼落字于聊天或 issue 引用）。
- [ ] plan 抬头含 `> 基于 spec：` 行，路径指向已落地的 spec。
- [ ] Handoff 11 字段全部填写、无空缺、无"待补"占位。
- [ ] Handoff `Status: ready`（实施 Session 可直接接管）。
- [ ] Handoff `Verification: 不要求 verify（规划 session 不跑 verify）`。
- [ ] Handoff `Prohibited Scope` 明确列出不可触碰的文件（包含 `scripts/scaffold-doctor.sh` / CI / 各 ADR / 其他规范的当前内容）。
- [ ] `git status --short` 仅显示新增的 spec + plan + 任意一份本 Session 报告，**不**包含任何已修改的脚本 / 测试 / 现有规约文件。
- [ ] `git diff --check` 退出 0（确认无 whitespace / EOF 警告）。

### 1.4 交接出口信号（物理落字版）

规划 Session 末尾在聊天输出一句：

> "规划 session 完成，交付物：spec at `docs/specs/2026-08-02-spec-and-plan-naming-check.md` + plan at `docs/plans/2026-08-02-spec-and-plan-naming-check.md`；Handoff 见 plan 末尾 `## Session Handoff`，11 字段齐，`Status: ready`。"

并将以下三个文件在 `git status` 中可见：

```text
docs/specs/2026-08-02-spec-and-plan-naming-check.md   (new)
docs/plans/2026-08-02-spec-and-plan-naming-check.md    (new)
.superpowers/sdd/task-c5-l2-planner.md                 (new)
```

**演练判定**：规划 Session 出口信号 = 11 字段 Handoff 的 `Status: ready` + spec/plan 双份物理独立 + 仅新增（未修改）其他文件。任何"未满足其中一项"则下一 Session 接管时**必须停止**（[session-handoff-protocol.md](../runbooks/session-handoff-protocol.md) "下一 Session 停止门禁"）。

### 1.5 规划 Session 的"禁止动作"边界

- 不得写 `scripts/check-spec-and-plan-naming.py` 或任何测试文件。
- 不得修改 `scripts/scaffold-doctor.sh`、`.github/`、`AGENTS.md`、`template/AGENTS.md`、任何 ADR 或既有 `docs/ai/**` 文档。
- 不得 `git add` / `git commit` / `git push`（commit 由用户在适当时机触发）。
- 不得写 `## 验证证据` 段（按 [ADR-0002](../../adr/0002-verify-hard-gate.md) 与 l2 runbook 第 1 Session 段"必跑 verify"列：规划 = **不要求**）。

---

## 2. 实施 Session 进口读取清单

**角色**：实施 Session（实施者 + 文档维护者）。
**模拟起点**：聊天消息收到"请按 plan 实施 `2026-08-02-spec-and-plan-naming-check`，在 worktree 内执行，本 Session 不带任何先前对话上下文"。

### 2.1 实施 Session 启动的"门禁检查"（前置停止条件）

**第 1 步：先走 Handoff 门禁**（按 [session-handoff-protocol.md](../runbooks/session-handoff-protocol.md) "下一 Session 停止门禁"）。读取 `docs/plans/2026-08-02-spec-and-plan-naming-check.md` 末尾的 `## Session Handoff`，逐条核对：

| # | 门禁 | 演练样本（已落地的真实 Handoff） | 通过条件 |
|---|---|---|---|
| 1 | 11 字段无缺失 | `Task Level` / `Phase` / `Status` / `Completed` / `Artifacts` / `Decisions` / `Assumptions` / `Open Questions` / `Verification` / `Next Allowed Actions` / `Prohibited Scope` 全部存在 | ✅ |
| 2 | `Status != blocked` | `Status: ready` | ✅ |
| 3 | `Artifacts` 路径全部存在 | `docs/specs/2026-08-02-spec-and-plan-naming-check.md` 已存在；`docs/plans/2026-08-02-spec-and-plan-naming-check.md` 已存在；`.superpowers/sdd/task-c5-l2-planner.md` 已存在 | ✅（用 `ls -la` 校验） |
| 4 | `Verification` 与 `Current Phase` 匹配 | `Current Phase: planning` + `Verification: 不要求 verify（规划 session 不跑 verify）` | ✅ |
| 5 | `Next Allowed Actions` 与 `Prohibited Scope` 边界清晰 | 既允许"实施 session 落地代码 + 测试"又禁止"修改 parent Plan C / scaffold-doctor / CI / 各 ADR" | ✅ |

**任一不通过 → 立即停止**。演练样本全部通过 → 允许进入实施。

**第 2 步：读 spec 与 plan 双份**（仅从仓库读）：

```bash
# 演练盘点命令（仅读，不写）
ls -la docs/specs/2026-08-02-spec-and-plan-naming-check.md
ls -la docs/plans/2026-08-02-spec-and-plan-naming-check.md
git log --oneline --all -- docs/specs/2026-08-02-spec-and-plan-naming-check.md || echo "not yet committed"
git diff --stat $(git merge-base HEAD origin/main 2>/dev/null || echo HEAD~1)..HEAD -- docs/specs docs/plans
```

读后**必须**恢复出以下信息（演练判定：以下 9 条信息全部能从仓库文件读出，缺一即为 Handoff 失败）：

| # | 信息 | 演练样本可恢复值 |
|---|---|---|
| 1 | 任务名 | `spec / plan 命名检查器` |
| 2 | 任务等级 | `L2`（来自 spec / plan Handoff `Task Level` + spec `## 行为` 末尾范围声明） |
| 3 | spec 路径 | `docs/specs/2026-08-02-spec-and-plan-naming-check.md` |
| 4 | plan 路径 | `docs/plans/2026-08-02-spec-and-plan-naming-check.md` |
| 5 | 主要生产文件 | `scripts/check-spec-and-plan-naming.py`（新建） |
| 6 | 主要测试文件 | `scripts/tests/test_check_spec_and-plan-naming.py`（新建） |
| 7 | 验证入口 | `python3 -m unittest discover -s scripts/tests -p 'test_check_spec_and_plan_naming.py' -v` + `python3 scripts/check-spec-and-plan-naming.py --root . --template` |
| 8 | 禁止范围 | 不修改 `scripts/scaffold-doctor.sh` / CI / `AGENTS.md` / `template/AGENTS.md` / 任何 ADR / 现有 `docs/ai/**` 文件 / 不引入任何第三方依赖 |
| 9 | 实施切片顺序 | TDD 6 步：写失败测试 → 跑 RED → 最小实现 → 跑 GREEN → 跑完整 verify → 写报告 |

**第 3 步：工作目录与分支确认**（[branch-strategy.md](../branch-strategy.md)）：

```bash
git status --short
git branch --show-current
git rev-parse --show-toplevel
```

演练样本期望：当前在 worktree `.worktrees/opt-ai-governance-v2-plans`，分支 `opt-ai-governance-v2-plans`；`git status --short` 仅含既有改动，不含"实施 session 自己未提交的"变更。

**第 4 步：依赖 / 工具 baseline 检查**（仅读）：

```bash
python3 --version
which python3
rg --version | head -1
```

演练期望：Python 3 ≥ 3.7（满足 `datetime.date.fromisoformat` 稳定接受）；`rg` 可用。

### 2.2 实施 Session 实际执行（纸面，不真的落盘）

演练**不**真写脚本 / 测试，**只**列出"如果实际执行会跑哪些命令、按什么顺序、退出码与关键输出"。

#### 步骤 1：写失败测试（RED）

新建 `scripts/tests/test_check_spec_and_plan_naming.py`，按 plan "步骤 1" 段给出的 `tempfile.TemporaryDirectory` + `subprocess.run` 骨架实现 6+ 用例。然后只跑这一个测试：

```bash
python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v
```

| 演练期望 | 退出码 | 关键输出 |
|---|---:|---|
| RED | 1 | `Ran 6 tests in 0.10s` / `FAILED (failures=N)` / `AssertionError: 0 != 1` |

#### 步骤 2：最小实现（GREEN）

新建 `scripts/check-spec-and-plan-naming.py`，按 plan "步骤 3" 给出骨架实现（argparse + glob + `datetime.date.fromisoformat` + kebab-case 正则）。再跑同样测试：

```bash
python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v
```

| 演练期望 | 退出码 | 关键输出 |
|---|---:|---|
| GREEN | 0 | `Ran 6 tests in 0.20s` / `OK` |

#### 步骤 3：完整 verify（覆盖项目根 `verify` 入口）

```bash
python3 -m unittest discover -s scripts/tests -p 'test_check_spec_and_plan_naming.py' -v
python3 scripts/check-spec-and-plan-naming.py --root . --template
python3 scripts/check-markdown-links.py --root . --template
python3 scripts/check-governance-consistency.py --root . --template
bash scripts/scaffold-doctor.sh --template
git diff --check
```

| 演练期望 | 退出码 | 关键输出 |
|---|---:|---|
| 单测 | 0 | `Ran 6 tests in 0.20s` / `OK` |
| 主检查器 | 0 | stdout 空 |
| 链接检查 | 0 | stdout 空 |
| 一致性检查 | 0 | stdout 空 |
| doctor | 0 | `Summary: 0 fail(s), 0 warning(s)` |
| `git diff --check` | 0 | stdout 空 |

#### 步骤 4：把 verify 结果写回 spec + plan 双份 `## 验证证据` 段

按 [ADR-0002](../../adr/0002-verify-hard-gate.md) 与 [l2-multi-session-runbook.md](../runbooks/l2-multi-session-runbook.md) "verify 落点细则" 段，**两份**均必填：

```markdown
<!-- 把 §2.2 步骤 3 的 6 行命令表写入 docsspecs/2026-08-02-spec-and-plan-naming-check.md 末尾 + docs/plans/2026-08-02-spec-and-plan-naming-check.md 末尾 -->
```

只填一份视为"未完整 verify 报告"。

#### 步骤 5：更新同一 plan 的 Handoff（status: ready → completed）

保留 11 字段 schema，把 `Status: ready` 改为 `Status: completed`，更新 `Verification` 段引用 `## 验证证据` 表的实际命令 / 退出码 / 关键输出。

#### 步骤 6：实施 Session 末端输出

> "实施 session 完成，交付物：code at `scripts/check-spec-and-plan-naming.py` + tests at `scripts/tests/test_check_spec_and_plan_naming.py`；验证证据 at `docs/specs/2026-08-02-spec-and-plan-naming-check.md#验证证据` 与 `docs/plans/2026-08-02-spec-and-plan-naming-check.md#验证证据` 双份均齐。"

### 2.3 实施 Session 接管判定

**结论**：演练 §2.1 的 5 个门禁步骤 + §2.2 的 6 个执行步骤**全部可仅凭仓库文件恢复并执行**——Handoff 11 字段 + spec + plan 双份的物理内容 + `git status` 提供了恢复任务所需的全部信息；不需要任何聊天上下文。

**度量**：

- 实施 Session 启动到第一行代码前的**最少读取** = 1 份 plan + 1 份 spec + 1 份 Handoff + 4 条 `git` / `python3` / `rg` baseline 命令 ≈ 6 步。
- 实施 Session 末端**最少输出** = 1 段 `## 验证证据` 表（6 行）+ 1 段 Handoff 状态变更 + 1 句"实施 session 完成"信号。

---

## 3. 评审 Session 消费结构

**角色**：评审 Session（审查者，默认新开 session）。
**模拟起点**：聊天消息"请评审 plan `2026-08-02-spec-and-plan-naming-check` 的实施交付物，本 Session 不带任何先前对话上下文"。

### 3.1 评审 Session 必读输入清单（仅从仓库恢复）

#### 3.1.1 diff / 改动概览

```bash
git diff --stat <base>..HEAD
git diff <base>..HEAD -- scripts/check-spec-and-plan-naming.py scripts/tests/test_check_spec_and_plan_naming.py
git diff <base>..HEAD -- docs/specs/2026-08-02-spec-and-plan-naming-check.md docs/plans/2026-08-02-spec-and-plan-naming-check.md
```

演练期望：评审从 `<base>..HEAD` 一段 diff 即恢复出"实施改了哪些文件、哪些字节、为什么改"。

#### 3.1.2 spec + plan 双份

```bash
# 评审只看两份文件本身，不读实施 Session 的中间对话 / 论文
less docs/specs/2026-08-02-spec-and-plan-naming-check.md
less docs/plans/2026-08-02-spec-and-plan-naming-check.md
```

#### 3.1.3 Handoff 11 字段

读 `docs/plans/2026-08-02-spec-and-plan-naming-check.md` 末尾 `## Session Handoff`，校验：

- `Status: completed`（与实施 Session 末端信号一致）。
- `Verification` 段引用 `## 验证证据` 表（不重复展开）。
- `Prohibited Scope` 与 `git diff` 改动集合**交集为空** —— 演练期望：diff 仅含 `scripts/check-spec-and-plan-naming.py`（新建）+ `scripts/tests/test_check_spec_and_plan_naming.py`（新建）+ `docs/specs/...spec-and-plan-naming...md` 的 `## 验证证据` 段（追加）+ `docs/plans/...spec-and-plan-naming...md` 的 `## 验证证据` 段（追加）+ `.superpowers/sdd/task-c5-l2-impl.md`（新增）；与 Prohibited Scope 列出的"scaffold-doctor / CI / 各 ADR / 既有 docs/ai 文档"**交集为空**。

#### 3.1.4 `## 验证证据` 段（spec + plan 双份均必填）

```bash
grep -n "## 验证证据" docs/specs/2026-08-02-spec-and-plan-naming-check.md
grep -n "## 验证证据" docs/plans/2026-08-02-spec-and-plan-naming-check.md
tail -30 docs/specs/2026-08-02-spec-and-plan-naming-check.md
tail -30 docs/plans/2026-08-02-spec-and-plan-naming-check.md
```

演练期望：两份文件均含 `## 验证证据` 段，且命令 / 退出码 / 关键输出 / 未跑项 4 列均齐，**两份间内容一致**（同一批命令的两次记录）。

#### 3.1.5 评审 checklist

按 [`docs/ai/checklists/review-checklist.md`](../checklists/review-checklist.md) 跑各项检查；不下钻到实施 Session 中间对话。

### 3.2 评审 Session 的消费结构（只需 5 类输入即完成审查）

```
┌─────────────────────────────────────────────────────────────┐
│  评审 Session 必读输入（5 类，不读实施 Session 中间对话）  │
├─────────────────────────────────────────────────────────────┤
│  1. git diff <base>..HEAD                                   │
│     → 改动文件清单 / 行数 / 改动范围                        │
│  2. spec（docs/specs/...）                                  │
│     → 目标 / 行为 / 非目标 / 验收                           │
│  3. plan（docs/plans/...）                                  │
│     → 文件清单 / 任务切片 / 命令 / 预期结果                 │
│  4. Handoff（plan 末尾 ## Session Handoff，11 字段）        │
│     → 当前阶段 / 状态 / 已完成 / 已交付 / 决策 / 假设 /    │
│        未决 / 验证 / 下一动作 / 禁止范围                    │
│  5. ## 验证证据 段（spec + plan 双份末尾）                  │
│     → 实际命令 / 退出码 / 关键输出 / 未跑项                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  评审 Session 必交付物                                       │
├─────────────────────────────────────────────────────────────┤
│  - 严重级别（Critical / Important / Minor）                 │
│  - 文件 + 行号 + 行为位置 + 风险说明 + 缺失验证或测试       │
│  - "测试盲区"清单（评审者必填，未发现也明确写"无"）        │
│  - "未跑项"清单（对照 spec + plan 双份 ## 验证证据）        │
│  - L2 规划特定检查：spec 与 plan 物理分离 / spec 先经用户   │
│    确认 / plan 抬头引用 spec / 实施 session 跑过 verify     │
│  - 评审结论：APPROVED / APPROVED_WITH_FOLLOWUPS / BLOCKED   │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 评审 Session 论文结论（演练样本）

> **评审结论**：APPROVED。
>
> 评审依据：
>
> 1. **改动范围符合 spec/plan**：diff 仅含 1 个新建生产脚本 + 1 个新建测试 + 2 份 spec/plan 的 `## 验证证据` 追加段 + 1 份实施报告（`.superpowers/sdd/task-c5-l2-impl.md`）；与 Handoff `Prohibited Scope` 交集为空。
> 2. **spec / plan 物理分离**：两份独立文件，plan 抬头含 `> 基于 spec：` 行；spec 状态 `draft` → 实施期间未变更。
> 3. **Handoff 11 字段齐**，`Status: completed`，`Verification` 段引用 `## 验证证据` 表。
> 4. **`## 验证证据` 段双份均齐**：命令 / 退出码 / 关键输出 / 未跑项 4 列齐；未跑项仅 1 条（`bash -n` 对 Python 不适用），原因对齐 paper 模板。
> 5. **测试盲区**：与 Task 5 L2 演练报告一致（invalid-root 行为仅断言退出码未断言 stderr；输出测试用 `assertIn` 未精确定位单行；无 `2026-02-30` / `2026-08-02-.md` / 空格 / 非 ASCII 名称 fixture；无 `--root` 缺省路径覆盖）。残余风险低，不阻塞 APPROVED。
> 6. **L2 特定检查**：spec 与 plan 物理分离 ✅；spec 先经用户确认（论文 brief 显式记录"合并规划 + 批准"为批准信号）✅；plan 抬头引用 spec ✅；实施 session 跑过 verify ✅。
>
> **未发现 Critical / Important finding**。Minor 见 §3.4。

### 3.4 评审提出的 Minor 改进建议（不阻塞 APPROVED）

1. `scripts/check-spec-and-plan-naming.py` 末尾、`scripts/tests/test_check_spec_and_plan_naming.py` 末尾缺 EOF newline；`git diff --check` 不报警，但符合仓库卫生习惯。
2. `## 验证证据` 段可考虑加 `## 批准` 段顺序检查（L3 任务专用，本任务为 L2 无需）。
3. 实施 Session 报告 `.superpowers/sdd/task-c5-l2-impl.md` 末尾"未跑项"仅 1 条，建议未来 L2 任务把"未跑项"拆出独立二级标题以便评审对照。

---

## 4. 演练判定指标

| 指标 | 期望 | 演练样本 |
|---|---|---|
| 规划 Session 出口信号是否清晰 | 11 字段 Handoff + 末端"session 完成"信号 | ✅ |
| 实施 Session 可从仓库恢复的最小读取步数 | ≤ 6 步 | ✅（1 份 plan + 1 份 spec + 1 份 Handoff + 4 条 baseline） |
| 实施 Session 末端输出是否完整 | 1 段 `## 验证证据` + 1 段 Handoff 状态变更 + 1 句信号 | ✅ |
| 评审 Session 消费结构是否独立 | 5 类输入（diff / spec / plan / Handoff / 验证证据）；不读实施 Session 中间对话 | ✅ |
| 评审 Session 必交付物是否齐 | 严重级别 / 测试盲区 / 未跑项 / L2 特定检查 / 结论 | ✅ |
| 接力边界是否被破坏 | 实施 Session 是否修改了 Prohibited Scope 列出的文件 | 否（diff 与 Prohibited Scope 交集为空） |
| 接力完整性是否被验证 | 3 个 Session 是否可仅凭仓库文件串行 | 是 |

---

## 5. 演练结论

**结论**：L2 三 Session 接力协议 + Handoff 11 字段 schema 在零对话历史的前提下可以**完整恢复**——规划 Session 的出口信号、实施 Session 的进口读取、评审 Session 的消费结构三段均成立。

**未发现新规则歧义**。本演练只验证既有协议的可执行性，不引入新规则。

**建议**（不自动成为硬门禁）：

1. 未来 L2 任务在实施 Session 启动时，可将 §2.1"门禁检查 5 步"作为"实施 Session 启动 checklist"补入 [`l2-multi-session-runbook.md`](../runbooks/l2-multi-session-runbook.md) 第 2 Session 段，作为可复制条目。
2. 评审 Session 的"5 类输入清单"（§3.1）可作为 [`review-checklist.md`](../checklists/review-checklist.md) 的"评审输入清单"小节附录用条目。

**演练产物**：本文件 + §3.3 评审结论（作为论文证据）。本演练**不**修改任何规范文件 / 任何 ADR / 任何运行手册 / 任何模板。
