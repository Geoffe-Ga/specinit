# Claude Agent Profiles

This directory contains specialized agent profiles for enforcing quality standards in AI-assisted development.

## Available Profiles

### 1. Quality Reviewer (`quality-reviewer.md`)
**Purpose**: Ruthlessly thorough code review enforcing world-class standards

**Use when**: Reviewing pull requests, checking code changes

**Example**:
```bash
# In Claude Code CLI
/load .claude/profiles/quality-reviewer.md
# Then: "Please review the changes in src/api/users.py"
```

**What it checks**:
- Code quality (complexity, function length, naming)
- Test coverage and quality
- Security vulnerabilities
- Architecture violations
- Documentation completeness

### 2. Test Generator (`test-generator.md`)
**Purpose**: Write comprehensive tests before implementation (TDD)

**Use when**: Creating new features, adding test coverage

**Example**:
```bash
# In Claude Code CLI
/load .claude/profiles/test-generator.md
# Then: "Generate tests for the User authentication feature"
```

**What it generates**:
- Happy path tests
- Edge case tests
- Error handling tests
- Security tests
- Property-based tests (when appropriate)

### 3. Security Auditor (`security-auditor.md`)
**Purpose**: Find and fix security vulnerabilities

**Use when**: Security reviews, before deployment, after dependency updates

**Example**:
```bash
# In Claude Code CLI
/load .claude/profiles/security-auditor.md
# Then: "Audit the authentication system for security issues"
```

**What it audits**:
- Authentication/authorization
- Input validation
- SQL injection
- XSS vulnerabilities
- CSRF protection
- Secrets management
- OWASP Top 10

## How to Use Profiles

### Claude Code CLI

```bash
# Method 1: Load profile explicitly
/load .claude/profiles/quality-reviewer.md
"Review the latest changes"

# Method 2: Reference in prompt
"Using the quality-reviewer profile, review src/api.py"
```

### Claude.ai Web Interface

1. Open the profile file in your editor
2. Copy the contents
3. Paste into Claude.ai chat
4. Ask your question

### Cursor/Other IDEs

Configure as a custom instruction or system prompt in your IDE settings.

## Workflow Examples

### Feature Development Workflow

```bash
# 1. Generate tests first (TDD)
/load .claude/profiles/test-generator.md
"Generate comprehensive tests for user registration feature"

# 2. Implement the feature
# (write code to make tests pass)

# 3. Security audit
/load .claude/profiles/security-auditor.md
"Audit the user registration implementation"

# 4. Code review before PR
/load .claude/profiles/quality-reviewer.md
"Review all changes in this branch"
```

### Bug Fix Workflow

```bash
# 1. Generate regression test
/load .claude/profiles/test-generator.md
"Create test that reproduces issue #123"

# 2. Fix the bug
# (implement fix)

# 3. Review the fix
/load .claude/profiles/quality-reviewer.md
"Review the bug fix for issue #123"
```

### Security Review Workflow

```bash
# Before major release
/load .claude/profiles/security-auditor.md
"Perform comprehensive security audit of the entire codebase"

# After dependency updates
/load .claude/profiles/security-auditor.md
"Check for new vulnerabilities introduced by dependency updates"
```

## Customization

You can customize these profiles for your project:

1. **Add project-specific rules**: Edit profiles to include your team's conventions
2. **Adjust thresholds**: Modify complexity limits, coverage requirements, etc.
3. **Add language-specific checks**: Include checks for your framework/language
4. **Create new profiles**: Copy existing profiles and modify for specialized needs

## Tips for Effective Use

1. **Be specific in your requests**: "Review authentication.py focusing on security" is better than "review this"
2. **Use appropriate profile**: Don't use security-auditor for simple refactoring
3. **Combine profiles**: Use test-generator then quality-reviewer for comprehensive coverage
4. **Save good reviews**: Keep examples of thorough reviews for reference
5. **Iterate**: If review isn't thorough enough, ask for more detail

## Integration with CI/CD

While these profiles are designed for interactive use, you can reference them in:
- Pre-commit hooks
- PR templates
- Code review checklists
- CI pipeline documentation

## Resources

- [Claude Code Documentation](https://claude.com/claude-code)
- [CLAUDE.md](../CLAUDE.md) - Project-specific development guide
- [AGENTS.md](../AGENTS.md) - Provider-agnostic AI agent instructions
