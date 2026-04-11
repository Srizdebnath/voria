# Setup for Contributors

Everything you need to set up Victory for local development and contribution.

## Prerequisites

Make sure you have installed:
- **Git** - Version control
- **Node.js** v16+ - JavaScript runtime
- **Python** v3.9+ - Python runtime
- **Rust** - For CLI development (install from https://rustup.rs/)

## Quick Start (5 minutes)

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/Victory.git
cd Victory

# 2. Add upstream
git remote add upstream https://github.com/Srizdebnath/Victory.git

# 3. Create a branch
git checkout -b feature/my-feature

# 4. Install dependencies
cd rust && cargo build && cd ..
cd python && pip install -e . && cd ..

# 5. Build and test
cd rust && cargo test && cd ..
cd python && pytest && cd ..

# 6. Make changes and commit
git commit -m "feat: add new feature"

# 7. Push and create PR
git push origin feature/my-feature
```

## Full Development Setup

### Step 1: Clone Repository

```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/Victory.git
cd Victory

# Add upstream for syncing
git remote add upstream https://github.com/Srizdebnath/Victory.git

# Verify remotes
git remote -v
```

### Step 2: Setup Rust Development

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Navigate to rust directory
cd rust

# Build debug version
cargo build

# Build release version (optimized)
cargo build --release

# Run tests
cargo test

# Format code
cargo fmt

# Lint code
cargo clippy

# Clean build artifacts
cargo clean

cd ..
```

### Step 3: Setup Python Development

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Navigate to python directory
cd python

# Install in development mode
pip install -e ".[dev]"

# Or install with all dependencies
pip install -e .

# Install additional development tools
pip install pytest pytest-asyncio black flake8 mypy

# Run tests
pytest -v

# Format code
black .

# Lint code
flake8 victory

# Type checking
mypy victory

# Clean cache
rm -rf .pytest_cache __pycache__

cd ..
```

### Step 4: Verify Installation

```bash
# Test Rust CLI
./target/debug/victory --help

# Test Python engine
python3 -m victory.engine --help

# Run integration test
echo '{"command":"plan","issue_id":1}' | python3 -m victory.engine
```

## Project Structure

```
victory/
├── .github/
│   ├── ISSUE_TEMPLATE/      # Issue templates
│   ├── workflows/           # GitHub Actions CI/CD
│   └── pull_request_template.md
├── rust/
│   ├── src/
│   │   ├── main.rs
│   │   ├── cli/mod.rs
│   │   ├── ipc/mod.rs
│   │   ├── orchestrator/mod.rs
│   │   ├── config/mod.rs
│   │   └── ui/mod.rs
│   ├── Cargo.toml
│   └── tests/
├── python/
│   ├── victory/
│   │   ├── core/
│   │   │   ├── llm/        # LLM providers
│   │   │   ├── github/     # GitHub integration
│   │   │   ├── patcher/    # Code patching
│   │   │   ├── executor/   # Test execution
│   │   │   └── agent/      # Main loop
│   │   ├── plugins/
│   │   ├── engine.py       # Main entry point
│   │   └── __init__.py
│   ├── setup.py
│   └── tests/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   ├── DEVELOPMENT.md
│   ├── README.md
│   └── ...
├── CODE_OF_CONDUCT.md
├── CONTRIBUTORS.md
├── README.md
└── package.json
```

## Common Tasks

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make your changes
# - Write code
# - Add tests
# - Update docs

# 3. Test your changes
cd rust && cargo test && cd ..
cd python && pytest && cd ..

# 4. Format and lint
cd rust && cargo fmt && cargo clippy && cd ..
cd python && black . && flake8 victory && cd ..

# 5. Commit with conventional commits
git add .
git commit -m "feat: add new feature

- Implementation details
- Test additions
- Documentation updates

Fixes #123"

# 6. Push
git push origin feature/my-feature

# 7. Create PR on GitHub
```

### Fixing a Bug

```bash
# 1. Create fix branch
git checkout -b fix/bug-description

# 2. Write test that reproduces bug
# (Optional: check tests still fail)

# 3. Fix the bug
# (Tests should now pass)

# 4. Commit with reference
git commit -m "fix: resolve issue with feature X

- Root cause
- How it's fixed
- Tests added

Fixes #456"

# 5. Push and create PR
git push origin fix/bug-description
```

### Updating Documentation

```bash
# 1. Create docs branch
git checkout -b docs/update-topic

# 2. Edit markdown files in /docs

# 3. Preview locally (if supported)

# 4. Commit
git commit -m "docs: update installation guide

- Clarified Python version requirement
- Added troubleshooting section
- Fixed typos"

# 5. Push and create PR
git push origin docs/update-topic
```

## Testing

### Run All Tests

```bash
# Rust tests
cd rust && cargo test && cd ..

# Python tests
cd python && pytest -v && cd ..
```

### Run Specific Tests

```bash
# Rust specific test
cd rust && cargo test test_name && cd ..

# Python specific test
cd python && pytest tests/test_file.py::test_name -v && cd ..
```

### Test Coverage

```bash
# Python coverage
cd python && pip install coverage && coverage run -m pytest && coverage report && cd ..
```

## Code Quality

### Format Code

```bash
# Rust
cd rust && cargo fmt && cd ..

# Python
cd python && black . && cd ..
```

### Lint Code

```bash
# Rust
cd rust && cargo clippy -- -D warnings && cd ..

# Python
cd python && flake8 victory && cd ..
```

### Type Checking

```bash
# Python
cd python && mypy victory --ignore-missing-imports && cd ..
```

## Syncing with Upstream

Keep your fork in sync:

```bash
# Fetch latest changes
git fetch upstream

# Switch to master
git checkout master

# Merge upstream changes
git merge upstream/master

# Push to your fork
git push origin master
```

## Before Submitting a PR

1. **Write tests** - Cover your changes
2. **Update docs** - Document new features/APIs
3. **Format code** - Run formatters
4. **Lint code** - Fix all warnings
5. **Test locally** - Run full test suite
6. **Rebase if needed** - Keep history clean
7. **Fill PR template** - Describe your changes

## Commit Message Guidelines

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code cleanup
- `perf`: Performance
- `ci`: CI/CD

**Example:**
```
feat(llm): add support for new model

- Implement model provider
- Add integration tests
- Update documentation

Closes #123
```

## Getting Help

- **Documentation**: Check [docs/](./docs/)
- **Issues**: Search [GitHub Issues](https://github.com/Srizdebnath/Victory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Srizdebnath/Victory/discussions)
- **Email**: srizd449@gmail.com

## Troubleshooting

### Rust Build Issues

```bash
# Update Rust
rustup update

# Clean and rebuild
cd rust && cargo clean && cargo build && cd ..
```

### Python Issues

```bash
# Reinstall dependencies
cd python && pip install -e . --force-reinstall && cd ..

# Check Python version
python3 --version  # Should be 3.9+
```

### Permission Issues

```bash
# On Linux/Mac
chmod +x ./target/debug/victory
chmod +x ./target/release/victory
```

## Next Steps

1. **Read CONTRIBUTING.md** - Guidelines for contributions
2. **Check good-first-issue** - Start with easier tasks
3. **Create an issue** - Discuss before starting work
4. **Ask questions** - Use discussions for help

---

**Happy contributing! 🚀**
