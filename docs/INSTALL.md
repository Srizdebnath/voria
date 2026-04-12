# Installation Guide

Complete instructions for installing and using voria.

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

##  Quick Install (Recommended)

### Using npm (Easiest)

```bash
# Install globally
npm install -g @voria/cli

# Verify installation
voria --version  # Should show v0.0.2

# Initialize in your project
cd your-project
voria --init
```

**That's it!** voria is now ready to use.

## 🔧 Alternative: Manual Installation from Source

### Step 1: Clone Repository

```bash
git clone https://github.com/Srizdebnath/voria.git
cd voria
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
voria --help

# Setup your LLM provider
voria setup-modal

# Setup GitHub access  
voria set-github-token

# List issues from a repository
voria list-issues owner/repo
```

Expected output:
```
⚡ voria - AI-Powered Bug Fixing

Usage: voria [OPTIONS] <COMMAND>

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

voria requires at least one LLM provider. Set up using `voria setup-modal`:

### Interactive Setup (Recommended)

```bash
# In your project directory
voria --init
```

This will guide you through:
1. ✅ Choose LLM provider (Modal, OpenAI, Gemini, Claude)
2. ✅ Enter API key
3. ✅ Set daily budget
4. ✅ Select test framework
5. ✅ Save configuration to `.voria.json`

### Manual Configuration

Edit `~/.voria/config.json` (created after `voria --init`):

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
sudo cp target/release/voria /usr/local/bin/

# Now run from anywhere
voria --version
```

### Create Shell Alias

```bash
# Add to ~/.bashrc or ~/.zshrc
alias voria="~/path/to/voria/target/release/voria"

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
COPY --from=builder /app/target/release/voria /usr/local/bin/
COPY python /app/python
WORKDIR /app
RUN pip install -e python/
ENTRYPOINT ["voria"]
```

Build and run:

```bash
docker build -t voria .
docker run -it voria --version
```

##  Post-Installation Verification

### Check All Components

```bash
# ✅ Check Rust CLI
./target/release/voria --version
./target/release/voria --help

# ✅ Check Python engine
python3 -c "import voria; print('Python OK')"

# ✅ Check NDJSON protocol
echo '{"command":"plan","issue_id":1}' | python3 -m voria.engine | head -1

# ✅ Check end-to-end
./target/release/voria plan 1
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
python3 test_voria_cli.py
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

voria uses stdin/stdout, not network ports, so this shouldn't occur. If you see it:

```bash
# Kill any hanging Python processes
pkill -f "python.*voria"
```

### "NDJSON protocol error"

```bash
# Clear any cached state
rm -rf ~/.voria/

# Reinstall
cd python && pip install -e . --force-reinstall
```

##  Installation Checklist

- [ ] Rust compiled successfully
- [ ] Python virtual environment created
- [ ] Python dependencies installed
- [ ] `voria --version` works
- [ ] `voria plan 1` works
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
- [GitHub Repository](https://github.com/Srizdebnath/voria)
- [Issue Tracker](https://github.com/Srizdebnath/voria/issues)
- [Email Contact](mailto:srizd449@gmail.com)

---

**Installation Complete!** Continue with [QUICKSTART.md](QUICKSTART.md) 🚀
