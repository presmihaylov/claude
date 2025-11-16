# GitHub Code Reviewer Skill

High signal, low noise code reviews. Flags only critical issues (bugs, security, performance, breaking changes) via succinct inline comments on specific lines.

## Quick Start

### 1. Review a Pull Request

Invoke the skill by asking Claude to review a PR:
```
"Review PR https://github.com/owner/repo/pull/123"
"Perform a code review on pull request #456"
"Analyze the changes in PR 789 and provide feedback"
```

### 2. What the Skill Does

The skill will automatically:
1. Fetch PR information and full diff
2. Gather system context by reading related files and searching for patterns
3. Identify **critical issues only**:
   - Bugs (crashes, logic errors, nil panics, unhandled errors)
   - Security (SQL injection, XSS, auth bypass, missing validation)
   - Performance (N+1 queries, inefficient algorithms, memory leaks)
   - Breaking changes (API incompatibilities, migration issues)
   - Critical architectural violations (layer separation breaks)
4. Leave succinct inline comments on specific lines (1-2 lines each)
5. Submit as **COMMENT only** (no approve/reject - humans make that decision)

**Skips**: Style, formatting, naming, nits, minor improvements, positive feedback

## Available Scripts

### get_pr_info.py
Fetches comprehensive PR metadata including title, description, files changed, and existing reviews.

```bash
python3 scripts/get_pr_info.py <pr_url_or_number>
```

**Output**: JSON with PR details including:
- Title, body, state, author
- Head and base branch information
- Commit SHA
- List of changed files with line additions/deletions
- Existing reviews

### get_pr_diff.py
Retrieves the unified diff for the pull request.

```bash
# Get full diff
python3 scripts/get_pr_diff.py <pr_url_or_number>

# Get diff for specific file
python3 scripts/get_pr_diff.py <pr_url_or_number> --file path/to/file.go
```

**Output**: Unified diff format showing all changes

### submit_review.py
Submits a complete review with multiple inline comments at once.

```bash
python3 scripts/submit_review.py <pr_number> \
  --repo owner/repo \
  --comments-file /tmp/pr-<number>-review.json \
  --event COMMENT \
  --body "Optional summary"
```

**Event type**: Always `COMMENT` (commentary only, no approve/reject)

**Comments file location**: Create in `/tmp/pr-<number>-review.json` to avoid cluttering working directory

**Comments file format** (see `example-review.json`):
```json
[
  {
    "path": "src/services/user.service.ts",
    "line": 42,
    "body": "bug: Null pointer exception if user.profile is undefined"
  },
  {
    "path": "src/db/queries.ts",
    "line": 50,
    "start_line": 48,
    "body": "performance: N+1 query - fetch with single query"
  }
]
```

## Review Philosophy: High Signal, Low Noise

### Core Principle

**Only flag critical issues that materially affect correctness, security, or performance.**

Skip style, naming, formatting, minor improvements, and positive feedback. This is surgical code review, not comprehensive nitpicking.

### What Makes This Different

1. **Contextual**: Reads related files, searches patterns, understands architecture before flagging issues
2. **Selective**: Only flags bugs, security holes, performance problems, and breaking changes
3. **Succinct**: 1-2 line comments stating issue and impact, no verbose explanations
4. **Inline-First**: Comments on specific lines where issues exist, rarely uses summary comments
5. **Actionable**: Direct feedback on what's wrong and why it matters

### Review Process

```
1. Fetch PR diff
2. Gather system context (Read/Grep/Glob)
3. Identify critical issues ONLY
4. Generate succinct inline comments
5. Submit review (usually with no summary)
```

## What Gets Flagged

Only high-severity issues:

- ✅ **Bugs**: Nil panics, logic errors, unhandled errors, edge case failures
- ✅ **Security**: SQL injection, XSS, auth bypass, credential leaks, validation gaps
- ✅ **Performance**: N+1 queries, inefficient algorithms, memory/resource leaks
- ✅ **Breaking Changes**: API incompatibilities, migration issues
- ✅ **Critical Architecture**: Layer separation violations, major pattern breaks

## What Gets Skipped

Everything else:

- ❌ Style, formatting, naming conventions
- ❌ Minor improvements or refactoring suggestions
- ❌ Nits, typos, comment quality
- ❌ Positive feedback (unless exceptional bug prevention)
- ❌ Test coverage gaps (unless missing tests for critical paths)
- ❌ Code quality issues that don't cause bugs

## Example Usage

### Typical Review
```
User: "Review PR #123"

Claude: [Uses skill - finds 3 critical issues]
- Fetches PR diff
- Reads related files for context
- Identifies: 1 null pointer bug, 1 SQL injection, 1 N+1 query
- Creates /tmp/pr-123-review.json with 3 inline comments
- Submits review with no summary comment
```

### Clean PR (No Issues)
```
User: "Review PR #456"

Claude: [Uses skill - finds no critical issues]
- Analyzes changes in context
- Finds no bugs, security issues, or performance problems
- Does NOT submit review (nothing to flag)
- Reports: "No critical issues found"
```

### Security-Focused Review
```
User: "Review PR #789 for security issues"

Claude: [Uses skill - security emphasis]
- Checks for injection vulnerabilities
- Validates auth/authorization
- Looks for credential exposure
- Submits review only if security issues found
```

## Common Critical Patterns

**Flag only if violation causes actual bug/security/performance issue:**

### Backend/API - Critical Issues
- ❗ Missing authentication/authorization checks (security)
- ❗ SQL injection via string concatenation (security)
- ❗ Unhandled errors or silent error swallowing (hides failures)
- ❗ Missing null/nil checks causing crashes
- ❗ Resource leaks (unclosed connections, file handles)
- ❗ N+1 database queries (performance)

### Frontend - Critical Issues
- ❗ XSS vulnerabilities from unescaped user input (security)
- ❗ Type safety bypassed (runtime errors)
- ❗ Missing error boundaries (crashes)
- ❗ Infinite render loops or memory leaks

### Database - Critical Issues
- ❗ SQL injection vulnerabilities
- ❗ Missing indexes on queried columns (performance)
- ❗ Missing data validation allowing bad data

**Skip**: Code style, naming conventions, formatting, or patterns that don't cause actual issues

## Requirements

- **GitHub CLI**: Install with `brew install gh` and authenticate with `gh auth login`
- **Python 3**: Already installed on most systems
- **Repository Access**: Must have read access to the repository being reviewed
- **Authentication**: GitHub CLI must be authenticated

## Tips for Best Results

1. **Just provide PR number/URL** - skill handles the rest
2. **Specify focus if desired** - "focus on security" or "check for performance issues"
3. **Expect selective feedback** - no comments means no critical issues found
4. **Inline comments only** - look for comments on specific lines, not PR summary

## Example Review Comments

See `example-review.json` for samples showing the succinct inline comment style.

## Skill Architecture

```
.claude/skills/github-code-reviewer/
├── SKILL.md              # Skill definition and instructions
├── README.md             # This file
├── example-review.json   # Sample review comments
└── scripts/
    ├── get_pr_info.py    # Fetch PR metadata
    ├── get_pr_diff.py    # Get unified diff
    └── submit_review.py  # Submit review with inline comments
```

## Troubleshooting

### "gh: command not found"
Install GitHub CLI: `brew install gh`

### "authentication required"
Authenticate: `gh auth login`

### "permission denied"
Ensure you have read access to the repository

### "PR not found"
Verify the PR number and repository are correct
