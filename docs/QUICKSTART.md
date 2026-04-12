# Quick Start Guide

Get voria running in 5 minutes or less!

##  5-Minute Setup

### 1. Install (2 minutes)

```bash
# Install globally from npm
npm install -g @srizdebnath/voria

# Verify
voria --version
```

### 2. Configure LLM Provider (1 minute)

```bash
# Setup Modal (FREE and easy!)
voria setup-modal your_modal_api_key

# Or get prompted for token
voria setup-modal
```

### 3. Setup GitHub Access (1 minute)

```bash
voria set-github-token
# Paste your GitHub Personal Access Token
```

### 4. List Issues (1 minute)

```bash
# List issues from any repository
voria list-issues owner/repo

# Or with full GitHub URL
voria list-issues https://github.com/owner/repo
```

**✅ That's it! voria is ready.**

##  Common Commands

### List Issues in a Repository

```bash
# Using owner/repo format
voria list-issues ansh/voria

# Using GitHub URL
voria list-issues https://github.com/ansh/voria

# Interactive mode
voria list-issues  # Will prompt for repo
```

### Fix a GitHub Issue

```bash
# Fix issue with repo specified
voria fix 42 ansh/voria

# Fix with GitHub URL
voria fix 42 https://github.com/ansh/voria

# Interactive mode
voria fix 42  # Will prompt for repo
```

### Plan out a Fix

```bash
# Plan how to fix an issue by ID
voria plan 123

# Apply a patch after planning
voria apply /path/to/patch.diff
```

### Show Help

```bash
voria --help              # General help
voria fix --help          # Command-specific help
voria list-issues --help  # List issues help
```

##  LLM Providers

voria supports multiple providers. Set one up during setup:

### 1. Modal (Easiest - Free tier)

```bash
# Get key from https://platform.openai.com/
export OPENAI_API_KEY="sk-..."
```

### 3. Google Gemini (Fast & Affordable)

```bash
# Get key from https://makersuite.google.com/app/apikey
export GOOGLE_API_KEY="..."
```

### 4. Anthropic Claude (Highest Quality)

```bash
# Get key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="..."
```

##  Project Structure (What You Got)

```
voria/
├── rust/              # CLI (Rust)
├── python/            # Engine (Python)
├── docs/              # Documentation (You are here!)
└── target/            # Build output
```

##  Verify Everything Works

```bash
# Test CLI
./target/release/voria --version
./target/release/voria --help

# Test Python engine
python3 -m voria.engine

# Test end-to-end
./target/release/voria plan 1
```

##  Next Steps

1. **Learn usage** → Read [USER_GUIDE.md](USER_GUIDE.md)
2. **See examples** → Check [EXAMPLES.md](EXAMPLES.md)
3. **Understand it** → Study [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Contribute** → Follow [CONTRIBUTING.md](CONTRIBUTING.md)

##  Quick Links

- [Full Installation](INSTALL.md)
- [User Guide](USER_GUIDE.md)
- [Examples](EXAMPLES.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [GitHub](https://github.com/Srizdebnath/voria)

## ❓ Common Issues

### Command not found
```bash
# Make sure you're in the right directory
cd voria
./target/release/voria --version
```

### LLM not working
```bash
# Verify configuration
python3 -m voria.core.setup

# Or set environment variable
export OPENAI_API_KEY="your-key-here"
```

### Python import error
```bash
# Reinstall Python package
cd python
pip install -e .
cd ..
```

---

**Ready to go deeper?** → [USER_GUIDE.md](USER_GUIDE.md) 🚀
