# Git Credential Security Plan for PR #48

## Problem Statement

Need to authenticate `git push` to GitHub using a token. Current approach using `GIT_USERNAME` and `GIT_PASSWORD` environment variables is **incorrect** - these are not standard git variables and will be ignored.

## Security Requirements

1. **Never log credentials** - Must not appear in logs, stdout, stderr, or error messages
2. **No command-line exposure** - Avoid passing credentials as CLI arguments (visible in process list)
3. **No file storage** - Don't write credentials to disk temporarily
4. **Proper cleanup** - Ensure credentials are cleared from memory after use
5. **Audit trail** - All approaches must pass bandit security checks (ruff S rules)

## Git Authentication Methods (Research)

### Option 1: GIT_ASKPASS (Current - INCORRECT)
```python
env["GIT_ASKPASS"] = "echo"
env["GIT_USERNAME"] = "x-access-token"
env["GIT_PASSWORD"] = token
```
**Status:** ❌ INCORRECT - GIT_USERNAME and GIT_PASSWORD are not standard git environment variables

### Option 2: Credential Helper with stdin
```python
# Create helper script that reads from stdin
helper_script = f"""#!/bin/sh
echo "username=x-access-token"
echo "password={token}"
"""
# Use git credential helper
env["GIT_ASKPASS"] = "/path/to/helper"
```
**Status:** ❌ INSECURE - Token embedded in script, written to disk

### Option 3: URL-Embedded Credentials
```python
# For HTTPS URLs: https://x-access-token:TOKEN@github.com/owner/repo
parsed = urlparse(repo_url)
if parsed.scheme in ("https", "http"):
    authenticated_url = f"{parsed.scheme}://x-access-token:{token}@{parsed.netloc}{parsed.path}"
    subprocess.run(["git", "push", "-u", authenticated_url, "main"], ...)
```
**Security Concerns:**
- ✅ Standard git mechanism, widely used
- ⚠️ Token visible in process list during execution (short-lived)
- ⚠️ Token could appear in error messages if push fails
- ⚠️ Git may cache URL in .git/config (needs cleanup)

### Option 4: Git Credential Store (Temporary)
```python
# Use git's credential.helper with cache
subprocess.run(["git", "config", "credential.helper", "cache --timeout=30"])
# Fill credential cache via stdin
subprocess.run(
    ["git", "credential", "fill"],
    input=f"protocol=https\nhost=github.com\nusername=x-access-token\npassword={token}\n",
    ...
)
# Then push normally
subprocess.run(["git", "push", "-u", "origin", "main"])
```
**Status:** ⚠️ COMPLEX - Requires multiple steps, harder to cleanup

### Option 5: SSH with Deploy Keys
**Status:** ❌ OUT OF SCOPE - Requires SSH key setup, not using token

## Recommended Approach

**Option 3: URL-Embedded Credentials** with security hardening:

### Implementation Plan

1. **Parse and validate repo URL** (already implemented in `_validate_repo_url`)
2. **Inject credentials only for HTTPS/HTTP schemes**
3. **Use capture_output=True** to prevent token leakage in terminal
4. **Clean up git config** after push to remove any cached URL
5. **Redact token from error messages** if push fails

### Security Mitigations

```python
def _setup_github_remote_and_push(self, repo_url: str, token: str) -> None:
    # Parse URL
    parsed = urlparse(repo_url)

    # Only inject credentials for HTTPS (SSH doesn't need it)
    if parsed.scheme in ("https", "http"):
        # Build authenticated URL
        authenticated_url = (
            f"{parsed.scheme}://x-access-token:{token}@"
            f"{parsed.netloc}{parsed.path}"
        )
    else:
        # SSH or git:// - use as-is
        authenticated_url = repo_url

    try:
        # Push with credentials, capture output to prevent leaks
        result = subprocess.run(
            ["git", "push", "-u", authenticated_url, "main"],
            cwd=self.project_path,
            capture_output=True,  # CRITICAL: prevent token in terminal
            check=True,
            timeout=300,
        )
    except subprocess.CalledProcessError as e:
        # Redact token from error message
        error_msg = str(e.stderr.decode() if e.stderr else e)
        if token in error_msg:
            error_msg = error_msg.replace(token, "***REDACTED***")
        raise RuntimeError(f"Git push failed: {error_msg}") from e
    finally:
        # Clean up: remove any cached credentials from git config
        subprocess.run(
            ["git", "config", "--unset", "credential.helper"],
            cwd=self.project_path,
            capture_output=True,
            check=False,  # OK if not set
        )
```

## Security Checklist

- [ ] Verify bandit/ruff S rules pass
- [ ] Confirm token never appears in logs
- [ ] Test that subprocess.run with capture_output prevents terminal output
- [ ] Verify git config cleanup removes any URL caching
- [ ] Test error path redaction with intentional push failure
- [ ] Review for timing attacks (none identified)
- [ ] Confirm no credentials written to disk

## Alternative: Git Credential Helper via Pipe

If URL approach fails security review, we can use git's credential helper with a pipe:

```python
# Write helper that outputs to stdout
helper = f"""#!/bin/sh
cat << EOF
username=x-access-token
password={token}
EOF
"""

# Use process substitution to avoid file
env["GIT_ASKPASS"] = helper  # Won't work, needs file path
```

**Status:** ❌ Requires file on disk, violates requirement #3

## Testing Strategy

1. **Unit test:** Mock subprocess.run, verify authenticated URL format
2. **Integration test:** Test with invalid token, verify error redaction
3. **Manual test:** Push to real repo, verify success
4. **Security test:** Check process list during push (ps aux | grep git)
5. **Cleanup test:** Verify git config clean after push

## Decision

**Proceed with Option 3 (URL-Embedded Credentials)** because:
- ✅ Standard git mechanism (used by GitHub Actions, CI tools)
- ✅ No disk I/O required
- ✅ Short-lived process exposure (seconds)
- ✅ Can mitigate error message leaks with redaction
- ✅ Cleanup is straightforward
- ✅ Widely used in industry (GitHub CLI, git-credential-cache)

**Rejection reasons for other options:**
- Option 1: Doesn't work (wrong env vars)
- Option 2: Writes token to disk
- Option 4: Too complex, harder to audit
- Option 5: Out of scope (SSH keys)

## Implementation Steps

1. Read current implementation in orchestrator.py:577-590
2. Replace environment variable approach with URL-embedded credentials
3. Add capture_output=True
4. Add token redaction in error handler
5. Add cleanup in finally block
6. Run security linter (ruff check with S rules)
7. Add test for error redaction
8. Manual verification with real push

## Security Sign-off

This plan must be reviewed before implementation. All security concerns must be addressed.

---

**Prepared by:** Claude (Code Review Response)
**Date:** 2025-12-23
**Status:** PENDING APPROVAL
