#!/usr/bin/env bash
# scripts/tests/worktree-add-test.sh
#
# Integration tests for scripts/worktree-add.sh and
# scripts/hooks/rewrite-worktree-add.sh using `mktemp -d` git fixtures.
#
# Each scenario uses a fresh `git init` temp repo; no shared state.
# The wrapper resolves `repo_root` via `git rev-parse --show-toplevel`
# from cwd, so each wrapper invocation must `cd` to its temp repo first.
# Cleanup runs `git worktree remove --force` and `git branch -D` for any
# wrapper-created branches before `rm -rf` of the temp dir.
#
# Scenarios (L1+ governance gate):
#   1. legal path + legal branch prefix       -> success + .worktreeinclude propagated
#   2. path outside .worktrees/               -> exit 1
#   3. illegal branch prefix (feature/foo)    -> exit 1
#   4. missing .worktreeinclude               -> no error
#   5. empty .worktreeinclude                 -> no error
#   6. comment lines starting with `#`        -> silently skipped
#   7. missing source file in .worktreeinclude -> silently skipped (bonus)
#   8. hook rewrites standalone `git worktree add` -> allow + wrapper cmd (bonus)
#   9. hook denies `git -C <dir> worktree add` -> deny (bonus)
#  10. hook denies composite `git worktree add && ...` -> deny (bonus)
#  11. hook allows non-`git worktree add` commands -> exit 0, no output (bonus)

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/worktree-add.sh"
HOOK="$REPO_ROOT/scripts/hooks/rewrite-worktree-add.sh"

PASS_COUNT=0
FAIL_TOTAL=0

record_pass() {
  printf '  PASS  %s\n' "$1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

record_fail() {
  printf '  FAIL  %s\n' "$1"
  FAIL_TOTAL=$((FAIL_TOTAL + 1))
}

TMPDIR_LATEST=""

cleanup() {
  local tmp="$TMPDIR_LATEST"
  if [ -n "$tmp" ] && [ -d "$tmp" ]; then
    if [ -d "$tmp/.worktrees" ]; then
      for wt in "$tmp/.worktrees"/*; do
        [ -d "$wt" ] || continue
        git -C "$tmp" worktree remove --force "$wt" >/dev/null 2>&1 || true
      done
    fi
    git -C "$tmp" branch --format='%(refname:short)' 2>/dev/null \
      | grep -E '^(feat|fix|opt|docs|refactor|chore|test)/' \
      | while IFS= read -r br; do
          git -C "$tmp" branch -D "$br" >/dev/null 2>&1 || true
        done
    rm -rf "$tmp"
  fi
}

make_temp_repo() {
  local tmp
  tmp=$(mktemp -d)
  git init -q -b main "$tmp" >/dev/null 2>&1
  git -C "$tmp" config user.email "test@example.com"
  git -C "$tmp" config user.name "Test"
  git -C "$tmp" config commit.gpgsign "false"
  printf '# Test Repo\n' > "$tmp/README.md"
  git -C "$tmp" add README.md
  git -C "$tmp" commit -q -m "init"
  printf '%s' "$tmp"
}

# Run a command from inside TMPDIR_LATEST; return its exit code.
# `cd` is wrapped in a subshell so the parent script's cwd is unaffected,
# so record_pass / record_fail keep updating the parent's PASS_COUNT.
run_in_tmp() {
  ( cd "$TMPDIR_LATEST" && "$@" )
}

# ---------------- Scenario 1 ----------------
echo "[Scenario 1] legal path + legal branch prefix -> create + .worktreeinclude propagated"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
printf '.env.local\n' > "$TMPDIR_LATEST/.worktreeinclude"
printf 'SECRET=foo\n' > "$TMPDIR_LATEST/.env.local"
wt_path="$TMPDIR_LATEST/.worktrees/feat-foo"
run_in_tmp bash "$WRAPPER" -b "feat/foo" "$wt_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
  if [ -f "$wt_path/.env.local" ] && [ "$(cat "$wt_path/.env.local")" = "SECRET=foo" ]; then
    record_pass "legal: worktree created + .env.local propagated"
  else
    record_fail "legal: worktree created but .env.local missing or wrong"
  fi
else
  record_fail "legal: wrapper returned exit $rc"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 2 ----------------
echo "[Scenario 2] path outside .worktrees/ -> exit 1"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
bad_path="$TMPDIR_LATEST/somewhere-else/feat-foo"
run_in_tmp bash "$WRAPPER" -b "feat/foo" "$bad_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 1 ]; then
  record_pass "outside-.worktrees: exit 1"
else
  record_fail "outside-.worktrees: expected exit 1, got $rc"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 3 ----------------
echo "[Scenario 3] illegal branch prefix (feature/foo) -> exit 1"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
wt_path="$TMPDIR_LATEST/.worktrees/feature-foo"
run_in_tmp bash "$WRAPPER" -b "feature/foo" "$wt_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 1 ]; then
  record_pass "illegal-prefix: exit 1"
else
  record_fail "illegal-prefix: expected exit 1, got $rc"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 4 ----------------
echo "[Scenario 4] missing .worktreeinclude -> no error"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
wt_path="$TMPDIR_LATEST/.worktrees/feat-foo"
run_in_tmp bash "$WRAPPER" -b "feat/foo" "$wt_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ] && [ -d "$wt_path" ]; then
  record_pass "missing-include: worktree created, exit 0"
else
  record_fail "missing-include: expected exit 0, got $rc"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 5 ----------------
echo "[Scenario 5] empty .worktreeinclude -> no error"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
: > "$TMPDIR_LATEST/.worktreeinclude"
wt_path="$TMPDIR_LATEST/.worktrees/feat-foo"
run_in_tmp bash "$WRAPPER" -b "feat/foo" "$wt_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ] && [ -d "$wt_path" ]; then
  record_pass "empty-include: worktree created, exit 0"
else
  record_fail "empty-include: expected exit 0, got $rc"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 6 ----------------
echo "[Scenario 6] comment lines (# ...) -> silently skipped"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
cat > "$TMPDIR_LATEST/.worktreeinclude" <<'EOF'
# this is a comment
.env.local

# another comment
EOF
printf 'SECRET=bar\n' > "$TMPDIR_LATEST/.env.local"
wt_path="$TMPDIR_LATEST/.worktrees/feat-bar"
run_in_tmp bash "$WRAPPER" -b "feat/bar" "$wt_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ] \
   && [ -f "$wt_path/.env.local" ] \
   && [ "$(cat "$wt_path/.env.local")" = "SECRET=bar" ]; then
  record_pass "comment-skip: .env.local copied; comments + blank line ignored"
else
  record_fail "comment-skip: wrapper exit=$rc or .env.local missing"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 7 (bonus) ----------------
echo "[Scenario 7] missing source file in .worktreeinclude -> silently skipped"
TMPDIR_LATEST=$(make_temp_repo)
trap 'cleanup' EXIT INT TERM
cat > "$TMPDIR_LATEST/.worktreeinclude" <<'EOF'
# this file does not exist anywhere
definitely/missing/file.txt
.env.local
EOF
printf 'SECRET=baz\n' > "$TMPDIR_LATEST/.env.local"
wt_path="$TMPDIR_LATEST/.worktrees/feat-baz"
run_in_tmp bash "$WRAPPER" -b "feat/baz" "$wt_path" >/dev/null 2>&1
rc=$?
if [ "$rc" -eq 0 ] \
   && [ -f "$wt_path/.env.local" ] \
   && [ ! -e "$wt_path/definitely" ] \
   && [ "$(cat "$wt_path/.env.local")" = "SECRET=baz" ]; then
  record_pass "missing-source: real file copied; missing entry skipped"
else
  record_fail "missing-source: wrapper exit=$rc or unexpected propagation"
fi
cleanup
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 8 (bonus: hook) ----------------
echo "[Scenario 8] hook: standalone 'git worktree add' -> rewrite to wrapper"
input='{"tool_input":{"command":"git worktree add -b feat/foo .worktrees/feat-foo"}}'
output=$(printf '%s' "$input" | bash "$HOOK" 2>&1)
rc=$?
parse_ok=$(printf '%s' "$output" | python3 -c "
import json, sys
try:
    obj = json.loads(sys.stdin.read())
except Exception as e:
    print('PARSE_FAIL:', e); sys.exit(1)
ok = (
    obj.get('hookSpecificOutput', {}).get('hookEventName') == 'PreToolUse'
    and 'worktree-add.sh' in obj.get('hookSpecificOutput', {}).get('updatedInput', {}).get('command', '')
    and 'feat/foo' in obj.get('hookSpecificOutput', {}).get('updatedInput', {}).get('command', '')
    and 'decision' not in obj
)
print('OK' if ok else 'MISMATCH')
sys.exit(0 if ok else 1)
" 2>&1)
if [ "$rc" -eq 0 ] && [ "$parse_ok" = "OK" ]; then
  record_pass "hook-rewrite: standalone command rewritten to wrapper"
else
  record_fail "hook-rewrite: rc=$rc parse=$parse_ok output=$output"
fi

# ---------------- Scenario 9 (bonus: hook) ----------------
echo "[Scenario 9] hook: 'git -C <dir> worktree add' -> deny"
input='{"tool_input":{"command":"git -C /tmp/somewhere worktree add -b feat/foo .worktrees/feat-foo"}}'
output=$(printf '%s' "$input" | bash "$HOOK" 2>&1)
rc=$?
parse_ok=$(printf '%s' "$output" | python3 -c "
import json, sys
try:
    obj = json.loads(sys.stdin.read())
except Exception as e:
    print('PARSE_FAIL:', e); sys.exit(1)
ok = (
    obj.get('decision') == 'block'
    and ('worktree-add.sh' in obj.get('reason', '') or 'pnpm worktree:add' in obj.get('reason', ''))
    and 'hookSpecificOutput' not in obj
)
print('OK' if ok else 'MISMATCH')
sys.exit(0 if ok else 1)
" 2>&1)
if [ "$rc" -eq 0 ] && [ "$parse_ok" = "OK" ]; then
  record_pass "hook-deny: 'git -C' form blocked with helpful reason"
else
  record_fail "hook-deny: rc=$rc parse=$parse_ok output=$output"
fi

# ---------------- Scenario 10 (bonus: hook) ----------------
echo "[Scenario 10] hook: composite 'git worktree add && echo ok' -> deny"
input='{"tool_input":{"command":"git worktree add -b feat/foo .worktrees/feat-foo && echo ok"}}'
output=$(printf '%s' "$input" | bash "$HOOK" 2>&1)
rc=$?
parse_ok=$(printf '%s' "$output" | python3 -c "
import json, sys
try:
    obj = json.loads(sys.stdin.read())
except Exception as e:
    print('PARSE_FAIL:', e); sys.exit(1)
ok = (
    obj.get('decision') == 'block'
    and 'composite' in obj.get('reason', '').lower()
)
print('OK' if ok else 'MISMATCH')
sys.exit(0 if ok else 1)
" 2>&1)
if [ "$rc" -eq 0 ] && [ "$parse_ok" = "OK" ]; then
  record_pass "hook-deny-composite: '&&' form blocked"
else
  record_fail "hook-deny-composite: rc=$rc parse=$parse_ok output=$output"
fi

# ---------------- Scenario 11 (bonus: hook) ----------------
echo "[Scenario 11] hook: non-git-worktree-add command -> silently allowed"
input='{"tool_input":{"command":"ls -la /tmp"}}'
output=$(printf '%s' "$input" | bash "$HOOK" 2>&1)
rc=$?
# Per spec: "exit 0, no output"
if [ "$rc" -eq 0 ] && [ -z "$output" ]; then
  record_pass "hook-allow-other: ls command silently allowed (exit 0, no output)"
else
  record_fail "hook-allow-other: rc=$rc output='$output'"
fi

# ---------------- Summary ----------------
echo ""
echo "=== Test Summary ==="
echo "Passed: $PASS_COUNT / 11"
echo "Failed: $FAIL_TOTAL / 11"
if [ "$FAIL_TOTAL" -eq 0 ]; then
  exit 0
else
  exit 1
fi