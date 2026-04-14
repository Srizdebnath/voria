# User Guide

Complete guide to using voria for automating bug fixes.

##  Overview

voria automates the process of fixing issues in your codebase. You describe a problem, and voria:

1. **Lists** issues from your repositories  
2. **Fetches** the issue details
3. **Generates** a fix using an AI LLM
4. **Applies** the patch to your code

##  Quick Example

```bash
# Setup your LLM provider (do once)
voria setup-modal your_token_here

# Setup GitHub access (do once)
voria set-github-token

# List all issues in a repo
voria list-issues owner/repo

# Fix a specific GitHub issue
voria fix 42 owner/repo

# Plan a fix for an issue
voria plan 42

# Apply a generated patch
voria apply patch-file.diff
```

---

##  Main Commands

### `voria setup-modal [TOKEN]`

Setup Modal API for AI-powered code generation.

**Usage:**
```bash
# With token provided
voria setup-modal sk-modal-your-key-here

# Or enter interactively
voria setup-modal
```

**What it does:**
- Saves Modal API key to `~/.voria/config.json`
- Sets Modal as your LLM provider
- Encrypts and secures your token

---

### `voria set-github-token`

Setup GitHub Personal Access Token for accessing repositories.

**Usage:**
```bash
voria set-github-token
# Paste your GitHub token when prompted
```

**What it does:**
- Saves GitHub token to `~/.voria/config.json`
- Enables access to private/public repositories
- Allows listing issues and creating pull requests

**Creating a GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full repository access)
4. Copy and paste the token

---

### `voria list-issues [REPO]`

List all open issues in a GitHub repository.

**Usage:**
```bash
# Using owner/repo format
voria list-issues ansh/voria

# Using full GitHub URL
voria list-issues https://github.com/ansh/voria

# Interactive mode (will prompt for repo)
voria list-issues
```

**Output:**
```
📋 Found 5 open issues in ansh/voria:

  #1 - Fix null pointer exception
       Labels: bug, critical
       https://github.com/ansh/voria/issues/1

  #2 - Add retry logic to API calls
       Labels: enhancement
       https://github.com/ansh/voria/issues/2
```

---

### `voria fix <ISSUE_NUMBER> [REPO]`

Fix a specific GitHub issue using AI.

**Usage:**
```bash
# With repo specified
voria fix 42 ansh/voria

# With full URL
voria fix 42 https://github.com/ansh/voria

# Interactive mode
voria fix 42
# Will prompt for repository

# With verbose output
voria fix 42 ansh/voria -v
```

**Workflow:**
```
1. Fetch issue title and description
2. Analyze the codebase
3. Generate a fix using LLM
4. Display the proposed patch
5. Show token usage and cost
```

**Options:**
- `-v, --verbose` - Show detailed output and debug information
- `--config <PATH>` - Use specific config file

### `voria --graph`

Advanced structural analysis and dependency visualization.

**Usage:**
```bash
voria --graph
```

**What it does:**
- Scans the entire codebase for dependencies and circular imports
- Generates a hierarchical tree view of folders and files
- Visualizes "imports" relationships at every level
- Calculates a **Risk Integrity Score** based on coupling and complexity
- Identifies **Hot Spots** (most complex/unstable modules)
- Provides actionable maintenance insights

**Output Example:**
```
🔭 Voria Multi-Level Dependency Tree
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 📁 src (3 files, 450 lines)
│   ├── 📄 main.rs → imports [cli.rs, config.rs]
│   └── 📁 cli (2 files, 300 lines)
│       └── 📄 mod.rs → imports [orchestrator.rs]
└── 📄 README.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ Ecosystem Health Index: 3.2/10.0 [EXCELLENT]
```

---

### `voria plan [ISSUE_ID]`

Plan how to fix a GitHub issue.

**Usage:**
```bash
# Analyze and propose a fix for issue #42
voria plan 42

# Verbose mode with details
voria plan 42 -v
```

**Output:**
```
🔍 Analyzing issue #42...
📝 Plan:
   - This is a simple type mismatch
   - Need to cast string to int
   - 1 file affected
   - Estimated complexity: LOW
```

---

### `voria apply <PATCH_FILE>`

Apply a previously-generated patch file.

**Usage:**
```bash
# Apply a patch
voria apply fix.patch

# Verbose output
voria apply fix.patch -v
```

**What it does:**
- Reads the patch file
- Applies changes to your code
- Shows modified files

---

### `voria test [NAME] [--list]`

Run codebase security audits, stress tests, and performance probes.

**Usage:**
```bash
# List all 50+ available tests
voria test --list

# Run a specific security scan (e.g., SQL Injection)
voria test sql_injection

# Perform a stress test
voria test cpu_stress
```

**Categories Include:**
- **Security (Pentesting):** SQLi, XSS, CSRF, JWT, SSRF, XXE, and 20+ more.
- **Production Resilience:** Deadlock detection, Race conditions, Unhandled exceptions.
- **Performance:** Latency baseline, P99 audits, Throughput benchmarks.
- **Stress Testing:** CPU/Memory saturation, concurrent user simulation.
- **Quality:** License compliance, dependency graph health.

**What it does:**
1. **Identifies** the test type (static analysis or dynamic probing).
2. **Analyzes** code context using LLMs for security patterns.
3. **Executes** runtime stress simulations for performance audits.
4. **Reports** detailed findings, severity, and recommended fixes.

---

##  Configuration

voria stores configuration in `~/.voria/config.json`:

```json
{
  "llm_provider": "openai",
  "llm_api_key": "sk-...",
  "llm_model": "gpt-4o",
  "github_token": "ghp_...",
  "daily_budget": 10.0,
  "test_framework": "pytest"
}
```

### Using Environment Variables

Instead of storing in config, you can use environment variables:

```bash
export MODAL_API_KEY=sk-modal-...
export GITHUB_TOKEN=ghp_...

# Or with other providers:
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

---

##  Examples

### Example 1: Fix a Simple Issue

```bash
# Setup (one time)
voria setup-modal
voria set-github-token

# List issues
voria list-issues owner/repo

# Fix issue #1
voria fix 1 owner/repo
```

### Example 2: Plan Before Fixing

```bash
# See what would be done
voria plan 42

# If it looks good, apply it
voria apply recommended-fix.patch
```

### Example 3: Batch Process Multiple Issues

```bash
# List all issues
voria list-issues owner/repo

# Fix multiple issues one by one
voria fix 1 owner/repo
voria fix 2 owner/repo
voria fix 3 owner/repo
```
3. Config file (`~/.voria/config.json`)
4. Defaults (OpenAI, gpt-4)

---

##  Setting Up LLM Providers

### OpenAI (Default)

```bash
# 1. Get API key from https://platform.openai.com/account/api-keys
# 2. Set key
export OPENAI_API_KEY=sk-...

# 3. Configure (optional, uses gpt-4 by default)
./target/release/voria plan "test" --llm openai --model gpt-4-turbo
```

**Cost:** ~$10-30/month for typical usage

### Claude (Anthropic)

```bash
# 1. Get API key from https://console.anthropic.com/
# 2. Set key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Use
./target/release/voria plan "test" --llm claude --model claude-3-sonnet
```

**Cost:** ~$5-15/month

### Gemini (Google)

```bash
# 1. Get API key from https://ai.google.dev/
# 2. Set key
export GOOGLE_API_KEY=...

# 3. Use
./target/release/voria plan "test" --llm gemini
```

**Cost:** ~$1-5/month (cheapest)

### Modal (Free)

```bash
# 1. Get API key from https://modal.com/
# 2. Set key
export MODAL_API_KEY=...

# 3. Use
./target/release/voria plan "test" --llm modal
```

**Cost:** Free (community tier) or ~$20/month

---

##  Understanding Costs

### Pricing by Provider

| Provider | Cost | Speed | Quality |
|----------|------|-------|---------|
| Gemini | $0.0001/1k | Fast | Good |
| OpenAI (GPT-4 Mini) | $0.03/1k | Medium | Very Good |
| Claude | $0.003/1k | Medium | Excellent |
| OpenAI (GPT-4 Turbo) | $0.03/1k | Slow | Best |
| Modal | Free/paid | Fast | Good |

### Cost Factors

Each fix typically costs:
- **Simple fix:** 10-50k tokens = $0.50-1.00
- **Medium fix:** 50-100k tokens = $1.00-3.00
- **Complex fix:** 100-200k tokens = $3.00-10.00

**Token usage depends on:**
- Repository size
- Issue complexity
- Number of iterations (failures and retries)
- LLM model choice

### Cost Control

```bash
# Set daily budget
export voria_DAILY_BUDGET=5.0

# Monitor spending
./target/release/voria token info

# Reduce context size to save tokens
./target/release/voria issue 42 --max-files 10

# Use cheaper LLM
./target/release/voria issue 42 --llm gemini  # 10x cheaper

# Limit iterations
./target/release/voria issue 42 --max-iterations 1
```

Typical monthly cost: **$5-30 depending on usage and LLM choice**

---

##  Working with Tests

### Supported Test Frameworks

| Language | Frameworks |
|----------|------------|
| Python | pytest, unittest, nose2, tox |
| JavaScript | Jest, Mocha, Jasmine, Vitest |
| Java | JUnit 4/5, TestNG |
| Go | testing, testify |
| Rust | cargo test |
| Ruby | RSpec, Minitest |

### Automatic Detection

voria automatically detects your test framework:

```bash
cd your-repo
./target/release/voria issue 42  # Detects pytest, jest, etc.
```

### Custom Test Command

```bash
# Specify test command explicitly
./target/release/voria issue 42 --test-cmd "npm test"

./target/release/voria issue 42 --test-cmd "pytest tests/ -xvs"

./target/release/voria issue 42 --test-cmd "cargo test --lib"
```

### Skip Testing

```bash
# Don't run tests (faster but less safe)
./target/release/voria issue 42 --skip-tests
```

### Test Failure Analysis

When tests fail, voria:

1. **Reads** the test output
2. **Analyzes** what went wrong
3. **Generates** a fix
4. **Reruns** tests (loop up to max-iterations)

Example:
```
❌ Tests failed (1/3 iterations)
    ERROR: TypeError in test_parse_url
    ...
🔧 Refining fix...
✅ Tests passed (2/3 iterations)
```

---

##  Iteration & Refinement

voria automatically improves fixes through iteration:

**How it works:**
1. Generate fix
2. Run tests
3. If tests fail → analyze failure → generate improved fix → go to step 2
4. Maximum 5 iterations (default: 3)

**Example:**
```
🔍 Iteration 1/3
  ✅ 8/9 tests pass → Need refinement

🔍 Iteration 2/3  
  ✅ 9/9 tests pass → SUCCESS
```

**Control iteration:**
```bash
# Try harder (up to 5 times)
./target/release/voria issue 42 --max-iterations 5

# Fast mode (only try once)
./target/release/voria issue 42 --max-iterations 1
```

---

##  Monitoring & Logging

### Check voria's Progress

```bash
# Verbose output (shows all steps)
./target/release/voria -v issue 42

# Very verbose (shows token count, API calls)
./target/release/voria -vv issue 42
```

### Token Usage

```bash
# Check token usage for this issue
./target/release/voria token info

# Reset daily counter (if needed)
./target/release/voria token reset
```

### Logs

voria logs are stored in `~/.voria/voria.log`:

```bash
# View recent logs
tail -f ~/.voria/voria.log

# Find errors
grep ERROR ~/.voria/voria.log
```

---

##  Safety & Best Practices

### Always Use Dry-Run First

```bash
# Propose first
./target/release/voria issue 42 --dry-run

# Review the proposed patch
git diff  # or look at voria's output

# Then apply
./target/release/voria issue 42
```

### Automatic Backups

voria automatically backs up files before patching:

```bash
~/.voria/backups/
├── file_1704067200.py  # Backup with timestamp
├── file_1704067201.py
└── ...
```

### Review PR Before Merging

voria creates PRs automatically, but always:

1. **Review** code changes in GitHub PR
2. **Check** tests pass in CI
3. **Ask** team for feedback if complex
4. **Merge** only when confident

### Rollback If Needed

```bash
# If voria's fix broke something:
git revert HEAD

# Or manually restore from backup
cp ~/.voria/backups/file_*.py restored_file.py
```

---

##  Troubleshooting

### "API Key Not Working"

```bash
# Verify key is set
echo $OPENAI_API_KEY  # Should not be empty

# Verify key format (starts with sk- for OpenAI)
echo $OPENAI_API_KEY | head -c 5

# Test key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | head
```

### "Tests Timeout"

```bash
# Increase timeout
./target/release/voria issue 42 --timeout 600  # 10 minutes

# Run tests manually to check they work
npm test  # or pytest, cargo test, etc.
```

### "No Issues Found"

```bash
# Ensure you're in a git repository
git status

# Ensure GitHub token is set
echo $GITHUB_TOKEN

# Specify repo explicitly
./target/release/voria issue 42 --repo https://github.com/user/repo
```

### "Patch Fails to Apply"

```bash
# Check git status
git status

# Try fuzzy matching
./target/release/voria issue 42 --patch-strategy fuzzy

# Review the patch manually
voria issue 42 --dry-run
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more issues.

---

##  Learning Resources

- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Examples](EXAMPLES.md)** - Real-world usage scenarios
- **[FAQ](TROUBLESHOOTING.md)** - Common problems and solutions
- **[Architecture](ARCHITECTURE.md)** - How voria works internally
- **[Plugins](PLUGINS.md)** - Extend voria with custom capabilities

---

##  Best Practices

### Start Small

```bash
# Dry-run first
./target/release/voria issue 42 --dry-run

# Review output carefully
# Then proceed if it looks good
```

### Use Right Tool for the Job

```bash
# For well-defined issues
./target/release/voria issue 42

# For vague descriptions  
./target/release/voria plan "optimize database queries"

# For direct descriptions
./target/release/voria plan "Add type hints to utils.py"
```

### Monitor Costs

```bash
# Start with cheaper models
./target/release/voria issue 42 --llm gemini  # 10x cheaper

# Upgrade if needed
./target/release/voria issue 42 --llm claude  # Better quality
```

### Iterate Carefully

```bash
# Let voria refine
./target/release/voria issue 42 --max-iterations 3

# Monitor progress
./target/release/voria -v issue 42
```

---

##  Advanced Usage

### Batch Processing

```bash
# Fix multiple issues
./target/release/voria issue 42 43 45 46

# Fix all open issues
./target/release/voria issue --all
```

### Custom Hooks

Create `~/.voria/hooks/post-fix.sh`:

```bash
#!/bin/bash
# Run after voria creates PR
echo "New PR created: $1"
# Send notification, etc.
```

### Team Configuration

Team leads can create `voria.config.json` in repo root:

```json
{
  "team_budget": 50.0,
  "default_llm": "claude",
  "excluded_paths": ["tests/", "docs/"],
  "required_reviewers": ["@team-lead"]
}
```

---

**See Also:**
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
- [PERFORMANCE.md](PERFORMANCE.md) - Speed optimization
- [SECURITY.md](SECURITY.md) - Security best practices
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

**Join our WhatsApp Support Group:** [Click Here](https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE?mode=gi_t)
