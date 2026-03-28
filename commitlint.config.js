module.exports = {
  // Self-contained config — no external packages needed.
  // Shell hook at scripts/validate-commit-msg.sh is the primary enforcement.
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'test', 'refactor', 'chore', 'perf', 'ci', 'build', 'revert'],
    ],
    'type-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'type-empty': [2, 'never'],
  },
};
