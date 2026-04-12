# Security Best Practices

Essential security guidelines for using voria safely.

##  Protecting Your Credentials

### API Keys

**Never commit API keys:**
```bash
# ❌ DO NOT
echo "OPENAI_API_KEY=sk-xxx" >> .env
git add .env  # BAD!

# ✅ DO
echo ".env" >> .gitignore
export OPENAI_API_KEY="sk-xxx"  # Set in shell
```

**Use environment variables:**
```bash
# Set in ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-..."
export MODAL_API_KEY="token-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export GITHUB_TOKEN="ghp_..."
```

**Rotate credentials regularly:**
```bash
# Monthly reminder to rotate keys
# 1. Generate new key in provider console
# 2. Export new key: export OPENAI_API_KEY="sk-new-..."
# 3. Delete old key in provider console
```

### Configuration Files

**Restrict permissions:**
```bash
# voria automatically sets 0600
ls -la ~/.voria/providers.json
# Output: -rw------- (readable only by user)

# Never relax permissions
chmod 600 ~/.voria/providers.json  # Only this
chmod 644 ~/.voria/providers.json  # ❌ Never this
```

**Control file access:**
```bash
# Only your user can read config
stat ~/.voria/providers.json

# On shared systems
sudo chmod 700 ~/.voria  # Directory is private
```

##  Code Execution Safety

### voria Never Executes Arbitrary Code

voria's safety model:

```
Rust CLI (Trusted)
    ↓
    └─→ Executes system commands (git, pytest, npm, etc.)
    ← Controlled & logged
    
Python Engine (Untrusted LLM output)
    ↓
    └─→ ONLY generates text (patches, plans)
    ← Never executes anything
```

**Safe Operations:**
- ✅ Reading files
- ✅ Generating diffs
- ✅ Parsing test output
- ✅ LLM API calls

**Prevented Operations:**
- ❌ `eval()` or `exec()`
- ❌ System command execution from Python
- ❌ Installing packages
- ❌ File deletion

### Patch Validation

voria validates patches before applying:

```python
# What voria checks
- Does patch format match unified diff?
- Do line numbers make sense?
- Are file paths reasonable?
- No suspicious shell commands?
- No write to sensitive locations (/etc, /sys, etc)?
```

##  File System Safety

### Automatic Backups

Before EVERY file modification:
```bash
~/.voria/backups/
├── file_1_2026-04-10T09-35-42.bak
├── file_2_2026-04-10T09-35-42.bak
└── file_3_2026-04-10T09-35-42.bak
```

**Recovery:**
```bash
# Roll back if needed
cp ~/.voria/backups/file_1_* original_file
```

### Restricted Access

voria only modifies:
- ✅ Repository files (your project)
- ❌ System files (/etc, /usr, /sys)
- ❌ Hidden files (. prefix)
- ❌ Outside repository directory

##  Network Security

### TLS/HTTPS Only

voria uses HTTPS for all API calls:
```python
# All connections are encrypted
- https://api.openai.com/
- https://generativelanguage.googleapis.com/
- https://api.anthropic.com/
- https://api.github.com/
```

**Verify certificates:**
```bash
# voria uses system CA certificates
# Update trust store if needed:
# macOS: /etc/ssl/certs/
# Linux: /etc/ssl/certs/ca-certificates.crt
# Windows: Certificate Manager
```

### No Direct Proxy Settings

voria respects system HTTP proxy:
```bash
# Set system proxy (voria uses it automatically)
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="https://proxy.example.com:8443"
export NO_PROXY="localhost,127.0.0.1"

voria plan 1  # Uses proxy automatically
```

##  Authentication & Authorization

### GitHub Token Scopes

Minimal required scopes:
```
repo            # Read repository
repo:status     # Read commit status
public_repo     # If public repository only
```

**Never use `admin:repo_hook` or `admin:org_hook`**

**Create token:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select ONLY needed scopes
4. Set expiration (90 days recommended)
5. Save to `~/.voria/config.json`

### LLM API Key Security

**Least privilege:**
- ✅ Create API key specifically for voria
- ❌ Use main account key
- ✅ Set rate limits in provider console
- ❌ Unlimited spending

**Monitor usage:**
```bash
# Check spending
python3 -c "from voria.core.token_manager import TokenManager; m = TokenManager(); print(m.get_stats())"

# Set alerts in provider console
# - OpenAI: Cost alerts
# - Gmail: Billing notifications
```

##  Audit & Logging

### Operations Log

voria logs all operations:
```bash
# View logs
voria logs --follow

# Logs include:
# - Command executed
# - Files modified
# - LLM prompts (when verbose)
# - Test results
```

### Never Logged

For security, these are NEVER logged:
- ❌ API keys
- ❌ Credentials
- ❌ OAuth tokens
- ❌ Personal data from issues

##  Preventing Common Attacks

### 1. Prompt Injection

**Risk**: LLM generating malicious code

**Protection**:
- voria validates all generated patches
- Patches must be valid unified diffs
- Suspicious commands rejected

### 2. Man-in-the-Middle

**Risk**: API credentials intercepted

**Protection**:
- HTTPS/TLS for all network traffic
- Certificate pinning (recommended for production)
- Use VPN for shared networks

### 3. Supply Chain

**Risk**: Malicious package in dependencies

**Protection**:
- Pin dependency versions
- Audit dependency contents
- Use `pip-audit` to check for CVEs

```bash
pip install pip-audit
pip-audit --desc  # Check for vulnerabilities
```

### 4. Accidental Secret Exposure

**Risk**: Committing API keys

**Protection**:
- Always use environment variables
- Add to .gitignore
- Use secret management tools (e.g., 1Password, Vault)

```bash
# 1Password integration
op run -- voria plan 1  # Injects env vars securely
```

##  Security Checklist

- [ ] API keys in environment variables (not files)
- [ ] Config file permissions set to 0600
- [ ] GitHub token has minimal scopes
- [ ] Budget limits set in provider console
- [ ] No credentials in git history
- [ ] HTTPS used for all network calls
- [ ] Backups enabled (auto-backup before changes)
- [ ] Logs reviewed for suspicious activity
- [ ] Dependencies audited for CVEs
- [ ] Only access from trusted networks

##  Advanced Security

### Air-Gapped Setup (No Internet)

```bash
# For highly sensitive repos
# 1. Create patch locally: voria plan 1 --dry-run
# 2. Review patch manually
# 3. Apply patch manually: patch < voria.patch
# 4. Run tests locally: pytest
```

### Sandboxed Execution (Docker)

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -e .
USER nobody  # Non-root user
ENTRYPOINT ["python", "-m", "voria.engine"]
```

### Hardware Security Module (HSM)

For enterprise:
```bash
# Configure HSM for API key storage
# Work with security team for setup
```

## 📞 Security Issues

**Found a security vulnerability?**

1. **DO NOT** create a GitHub issue
2. Email: security@voria.dev (use a responsible disclosure process)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

**See Also:**
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) - Security decisions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [PERFORMANCE.md](PERFORMANCE.md) - Performance tuning
