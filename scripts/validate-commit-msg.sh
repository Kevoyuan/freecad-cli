#!/bin/bash
# install-hooks.sh — Install git hooks for conventional commits
# Run once: bash scripts/install-hooks.sh

set -e

HOOK_DIR=".git/hooks"
COMMIT_MSG_HOOK="$HOOK_DIR/commit-msg"

mkdir -p "$HOOK_DIR"

# Install commit-msg hook to validate conventional commits
cat > "$COMMIT_MSG_HOOK" << 'HOOK'
#!/bin/bash
# commit-msg — validate commit message format (conventional commits)
# Types: feat, fix, docs, test, refactor, chore, perf, ci, build, revert

commit_regex='^(feat|fix|docs|test|refactor|chore|perf|ci|build|revert)(\(.+\))?!?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "ERROR: Commit message does not follow conventional commit format."
    echo ""
    echo "Required format: <type>(<scope>): <subject>"
    echo "  type: feat, fix, docs, test, refactor, chore, perf, ci, build, revert"
    echo "  scope: optional module name (e.g., core, cli, tests)"
    echo "  subject: imperative mood, max 50 chars, no period"
    echo ""
    echo "Examples:"
    echo "  feat(core): add empty name validation"
    echo "  fix(cli): correct --format flag documentation"
    echo "  test(core): add tests for part create command"
    echo ""
    echo "Your commit message:"
    cat "$1"
    exit 1
fi
HOOK

chmod +x "$COMMIT_MSG_HOOK"
echo "Installed commit-msg hook to $COMMIT_MSG_HOOK"
