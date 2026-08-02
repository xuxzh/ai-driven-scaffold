#!/usr/bin/env bash
# scripts/worktree-add.sh — generic wrapper around `git worktree add`
#
# Two safety rules are enforced BEFORE delegating to real git, and files
# declared in the repo's `.worktreeinclude` are propagated AFTER git
# reports success.
#
# Rule 1 — path scope
#   The new worktree path MUST be under `<repo_root>/.worktrees/`. This
#   prevents accidentally creating worktrees outside the conventional
#   isolation directory, which would bypass the rest of the governance
#   flow (see docs/ai/branch-strategy.md).
#
# Rule 2 — branch prefix whitelist
#   If `-b` or `-B` is used to create a new branch, the branch name MUST
#   start with one of the prefixes below. The whitelist is the single
#   source of truth in docs/ai/branch-strategy.md; this script mirrors
#   that list verbatim. When the doc changes, this list MUST be updated
#   in lock-step — see task report for the current branch-strategy.md
#   divergence (slash vs. hyphen separator).
#
#   Whitelist (synced with docs/ai/branch-strategy.md):
#     feat/   fix/   opt/   docs/   refactor/   chore/   test/
#
# After `git worktree add` succeeds, the wrapper reads
# `<repo_root>/.worktreeinclude` line by line and copies each entry into
# the new worktree. Lines that are empty, start with `#`, or whose source
# file is missing are silently skipped — propagation failures must not
# block worktree creation itself.

set -u

# --- Resolve a path to its physical (symlink-resolved) form ---
# On macOS, `mktemp -d` returns paths under `/var/folders/...` while
# `git rev-parse --show-toplevel` (and `cd && pwd -P`) returns the canonical
# `/private/var/folders/...`. Naive string comparison breaks. We resolve both
# sides to physical paths before any prefix check.
#
# Strategy: walk up to the deepest existing ancestor, resolve that via
# `cd && pwd -P`, then append the non-existing suffix verbatim.
resolve_physical() {
  rt_p="$1"
  rt_rest=""
  while [ ! -e "$rt_p" ]; do
    rt_rest="/$(basename -- "$rt_p")$rt_rest"
    rt_p=$(dirname -- "$rt_p")
  done
  rt_resolved=$(cd "$rt_p" && pwd -P)
  printf '%s%s\n' "$rt_resolved" "$rt_rest"
}

# --- Resolve repo root from git itself (not from any caller-provided env) ---
# Per the governance rule: only `git rev-parse --show-toplevel` is authoritative.
repo_root_raw=$(git rev-parse --show-toplevel 2>/dev/null) || {
  printf 'worktree-add.sh: not inside a git working tree\n' >&2
  exit 1
}
repo_root=$(resolve_physical "$repo_root_raw")

# --- Parse args to extract: new path, new branch (if any) ---
# Walk the args in order, skipping `-b/-B <branch>` (each takes an arg) and
# `--detach` (no arg). The first positional after that is the path. Anything
# after `--` is commit-ish / extra args and we stop parsing there.
new_branch=""
new_path=""
path_seen=0
i=1
while [ "$i" -le "$#" ]; do
  arg="${!i}"
  case "$arg" in
    -b|-B)
      i=$((i + 1))
      if [ "$i" -le "$#" ]; then
        new_branch="${!i}"
      fi
      ;;
    --detach)
      ;;
    --)
      break
      ;;
    -*)
      # Unknown flag: let `git worktree add` reject it. We do not need to
      # know about every option to validate path / branch.
      ;;
    *)
      if [ "$path_seen" -eq 0 ]; then
        new_path="$arg"
        path_seen=1
      fi
      ;;
  esac
  i=$((i + 1))
done

if [ "$path_seen" -eq 0 ]; then
  printf 'worktree-add.sh: cannot determine target path from args\n' >&2
  printf 'Usage: worktree-add.sh [git-worktree-add-options] <path> [<commit-ish>]\n' >&2
  exit 2
fi

# --- Resolve absolute path anchored at repo_root, then to physical form ---
case "$new_path" in
  /*) abs_path="$new_path" ;;
  *)  abs_path="$repo_root/$new_path" ;;
esac
abs_path=$(resolve_physical "$abs_path")

# --- Rule 1: path must be under <repo_root>/.worktrees/ ---
expected_prefix="$repo_root/.worktrees/"
case "$abs_path" in
  "$expected_prefix"*)
    ;;
  *)
    printf 'worktree-add.sh: target path must be under %s (got: %s)\n' "$expected_prefix" "$abs_path" >&2
    exit 1
    ;;
esac

# --- Rule 2: new branch prefix (if -b/-B given) must be in whitelist ---
if [ -n "$new_branch" ]; then
  whitelisted=0
  for prefix in feat/ fix/ opt/ docs/ refactor/ chore/ test/; do
    case "$new_branch" in
      "$prefix"*) whitelisted=1; break ;;
    esac
  done
  if [ "$whitelisted" -eq 0 ]; then
    printf 'worktree-add.sh: branch prefix not in whitelist: %s\n' "$new_branch" >&2
    printf '  allowed prefixes: feat/ fix/ opt/ docs/ refactor/ chore/ test/\n' >&2
    printf '  whitelist source: docs/ai/branch-strategy.md (keep in sync)\n' >&2
    exit 1
  fi
fi

# --- Delegate to real git ---
# cd to repo_root so any relative paths in the original args resolve as
# the user expected (relative to the repo, not the caller's cwd).
cd "$repo_root"
git worktree add "$@"
git_rc=$?
if [ "$git_rc" -ne 0 ]; then
  exit "$git_rc"
fi

# --- Propagate `.worktreeinclude` entries ---
include_file="$repo_root/.worktreeinclude"
if [ ! -f "$include_file" ]; then
  exit 0
fi

while IFS= read -r entry || [ -n "$entry" ]; do
  # Strip trailing CR (Windows line endings)
  entry="${entry%$'\r'}"
  # Trim leading/trailing whitespace
  entry=$(printf '%s' "$entry" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
  case "$entry" in
    ''|\#*) continue ;;
  esac
  if [ ! -e "$repo_root/$entry" ]; then
    continue
  fi
  dest_parent=$(dirname -- "$abs_path/$entry")
  mkdir -p -- "$dest_parent"
  cp -R -- "$repo_root/$entry" "$dest_parent/"
done < "$include_file"

exit 0