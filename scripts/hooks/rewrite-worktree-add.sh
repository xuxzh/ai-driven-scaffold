#!/usr/bin/env bash
# scripts/hooks/rewrite-worktree-add.sh — optional Claude Bash hook adapter
#
# It rewrites a safely-recognizable standalone `git worktree add` invocation
# into the wrapper, and refuses (deny) any `git worktree add` whose form is
# not safe to silently rewrite.
#
# Behaviour matrix:
#   input                                  -> action
#   ----------------------------------------  ----------------------------
#   non-git-worktree-add command           -> allow (exit 0, no output)
#   standalone `git worktree add ...`      -> rewrite via wrapper (allow)
#   `git -C <dir> worktree add ...`        -> deny: suggest wrapper / pnpm
#   `git worktree add ... && ...` / `;`    -> deny: composite form
#   `git worktree add ... | ...`           -> deny: piped form
#   unusual whitespace (tab)               -> deny: not safe to rewrite
#
# Rules are defined in scripts/worktree-add.sh and docs/ai/branch-strategy.md;
# this hook is only an adapter and must stay in sync with both. When either
# changes, the deny reasons or detection patterns here may need updating.

set -u

# --- Locate the wrapper relative to this hook script ---
hook_dir="$(cd "$(dirname "$0")" && pwd)"
wrapper="$(cd "$hook_dir/.." && pwd)/worktree-add.sh"

# --- Read the hook payload from stdin ---
input="$(cat)"

# --- Run the python logic via a temp file ---
# python3 is already a dependency of check-markdown-links.py and
# check-governance-consistency.py in scripts/, so this adds nothing new.
# The temp file approach avoids shell-escaping gymnastics for an inline
# `python3 -c "..."` while keeping stdout JSON clean.
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT INT TERM

cat > "$TMP" <<'PYEOF'
import json, sys, re

wrapper_path = sys.argv[1]
raw = sys.argv[2]

try:
    obj = json.loads(raw)
except json.JSONDecodeError:
    sys.exit(0)

cmd = obj.get("tool_input", {}).get("command", "")
if not isinstance(cmd, str) or not cmd:
    sys.exit(0)

trimmed = cmd.strip()

# Detection: bare `git worktree add` form (no -C / -c / --git-dir / etc.)
is_bare_worktree_add = bool(re.match(r"^git worktree add(\s|$)", trimmed))

if not is_bare_worktree_add:
    # Non-bare form: if `worktree add` appears anywhere, deny (likely
    # `git -C <dir>`, `git -c <key>=<val>`, etc.); otherwise allow silently.
    if "worktree add" in trimmed:
        print(json.dumps({
            "decision": "block",
            "reason": "'git worktree add' with extra options (e.g. -C, -c, --git-dir) is not safe to silently rewrite. Use 'bash scripts/worktree-add.sh ...' from inside the target repo, or run 'pnpm worktree:add' if your project exposes that alias."
        }))
    sys.exit(0)

# Bare form: detect unsafe features -> deny
deny = None
if re.search(r"&&|;|\|", trimmed):
    deny = "composite 'git worktree add' (with &&, ;, or |) is not safe to silently rewrite. Split the command and call 'bash scripts/worktree-add.sh ...' (or 'pnpm worktree:add') separately."
elif "\t" in trimmed:
    deny = "unusual whitespace (tab) detected in 'git worktree add'. Run 'bash scripts/worktree-add.sh ...' (or 'pnpm worktree:add') from a clean shell."

if deny:
    print(json.dumps({"decision": "block", "reason": deny}))
    sys.exit(0)

# Safe form -> rewrite via wrapper
new_cmd = re.sub(r"^git worktree add ", "bash \"" + wrapper_path + "\" ", trimmed)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "updatedInput": {"command": new_cmd}
    }
}))
PYEOF

python3 "$TMP" "$wrapper" "$input"