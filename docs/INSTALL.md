# Installation Guide

Complete instructions for installing and using Victory.

##  Prerequisites

### For Global CLI Tool (Recommended)
- **Node.js 16+** - Get from [https://nodejs.org](https://nodejs.org)
- **npm 8+** - Comes with Node.js
- **Git** - For version control

### For Development/Contributing
- **Rust 1.70+** - Get from [https://rustup.rs](https://rustup.rs)
- **Python 3.9+** - Get from [https://python.org](https://python.org)
- **10+ GB disk space** - For dependencies and build artifacts

### Optional (for specific features)
- **pytest** - For Python test execution support
- **Docker** - For sandboxed test runs
- **GraphQL client** - For GitHub Enterprise

##  Quick Install (Recommended)

### Using npm (Easiest)

```bash
# Install globally
npm install -g @srizdebnath/victory

# Verify installation
victory --version  # Should show v0.0.1

# Initialize in your project
cd your-project
victory --init
```

**That's it!** Victory is now ready to use.

## 🔧 Alternative: Manual Installation from Source

### Step 1: Clone Repository

```bash
git clone https://github.com/Srizdebnath/Victory.git
cd victory
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# On Windows: venv\Scripts\activate
```

### Step 3: Install Python Package

```bash
cd python
pip install -e ".[dev]"
cd ..
```

**What gets installed:**
- httpx 0.24.0 - Async HTTP client
- aiofiles 23.0 - Async file operations
- pydantic 2.0+ - Data validation
- pytest 7.4+ - Testing framework (optional)
- black - Code formatter (optional)
- mypy - Type checker (optional)

### Step 4: Verify Installation

```bash
# Test the installation
victory --help

# Setup your LLM provider
victory setup-modal

# Setup GitHub access  
victory set-github-token

# List issues from a repository
victory list-issues owner/repo
```

Expected output:
```
⚡ Victory - AI-Powered Bug Fixing

Usage: victory [OPTIONS] <COMMAND>

Commands:
  setup-modal       Setup Modal API configuration
  set-github-token  Set GitHub Personal Access Token
  list-issues       List issues from a GitHub repository
  fix               Fix a specific GitHub issue
  plan              Plan how to fix an issue
  issue             Run full agent loop on an issue
  apply             Apply an existing plan
  help              Print this message or the help of the given subcommand(s)

Options:
  -v, --verbose          Verbose logging
  -c, --config <CONFIG>  Configuration file path
  -h, --help             Print help
  -V, --version          Print version
```

##  Configure LLM Providers

Victory requires at least one LLM provider. Set up using `victory setup-modal`:

### Interactive Setup (Recommended)

```bash
# In your project directory
victory --init
```

This will guide you through:
1. ✅ Choose LLM provider (Modal, OpenAI, Gemini, Claude)
2. ✅ Enter API key
3. ✅ Set daily budget
4. ✅ Select test framework
5. ✅ Save configuration to `.victory.json`

### Manual Configuration

Edit `~/.victory/config.json` (created after `victory --init`):

```json
{
  "provider": "openai",
      "api_key": "sk-...",
      "model": "gpt-5.4"
    },
    "modal": {
      "api_key": "token-...",
      "model": "zai-org/GLM-5.1-FP8"
    }
  }
}
```

### Option C: Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Modal
export MODAL_API_KEY="token-..."

# Google Gemini
export GOOGLE_API_KEY="..."

# Anthropic Claude
export ANTHROPIC_API_KEY="..."
```

##  System-Wide Installation

### Install to PATH

```bash
# Copy binary to system path
sudo cp target/release/victory /usr/local/bin/

# Now run from anywhere
victory --version
```

### Create Shell Alias

```bash
# Add to ~/.bashrc or ~/.zshrc
alias victory="~/path/to/victory/target/release/victory"

# Reload shell
source ~/.bashrc
```

## 🐳 Docker Installation

```dockerfile
FROM rust:1.70 as builder
WORKDIR /app
COPY . .
RUN cd rust && cargo build --release

FROM python:3.11
COPY --from=builder /app/target/release/victory /usr/local/bin/
COPY python /app/python
WORKDIR /app
RUN pip install -e python/
ENTRYPOINT ["victory"]
```

Build and run:

```bash
docker build -t victory .
docker run -it victory --version
```

##  Post-Installation Verification

### Check All Components

```bash
# ✅ Check Rust CLI
./target/release/victory --version
./target/release/victory --help

# ✅ Check Python engine
python3 -c "import victory; print('Python OK')"

# ✅ Check NDJSON protocol
echo '{"command":"plan","issue_id":1}' | python3 -m victory.engine | head -1

# ✅ Check end-to-end
./target/release/victory plan 1
```

### Run Test Suite

```bash
# Python tests
cd python
pytest -v

# Rust tests
cd ../rust
cargo test

# Full integration
cd ..
python3 test_victory_cli.py
```

##  Development Installation

If you plan to contribute:

```bash
# Install with dev dependencies
cd python
pip install -e ".[dev]"

# Install development tools
pip install black pyright pytest-cov

# Format code
black .

# Type check
pyright .

# Run all tests
pytest -v
```

##  Troubleshooting Installation

### "cargo not found"

```bash
# Install Rust
curl --proto '=https' --tlsvv0.0.1 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### "Python version too old"

```bash
# Check version
python3 --version

# Update with your package manager
brew install python3  # macOS
apt install python3.11  # Ubuntu
```

### "Port already in use"

Victory uses stdin/stdout, not network ports, so this shouldn't occur. If you see it:

```bash
# Kill any hanging Python processes
pkill -f "python.*victory"
```

### "NDJSON protocol error"

```bash
# Clear any cached state
rm -rf ~/.victory/

# Reinstall
cd python && pip install -e . --force-reinstall
```

##  Installation Checklist

- [ ] Rust compiled successfully
- [ ] Python virtual environment created
- [ ] Python dependencies installed
- [ ] `victory --version` works
- [ ] `victory plan 1` works
- [ ] LLM provider configured
- [ ] All tests passing
- [ ] Configuration file created

##  Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) to run your first command
2. Check [USER_GUIDE.md](USER_GUIDE.md) for detailed usage
3. See [EXAMPLES.md](EXAMPLES.md) for real-world scenarios
4. Join the community on GitHub

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Read [DEVELOPMENT.md](DEVELOPMENT.md)
- Search [GitHub Issues](https://github.com/Srizdebnath/Victory/issues)
- Open a new issue

---

**Installation Complete!** Continue with [QUICKSTART.md](QUICKSTART.md) 🚀
