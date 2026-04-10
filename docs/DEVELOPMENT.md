# Development Guide

Complete guide for setting up a development environment and contributing to Victory.

##  Quick Dev Setup

```bash
# 1. Clone repo
git clone https://github.com/Srizdebnath/Victory.git
cd victory

# 2. Set up Rust
rustup update

# 3. Build Rust
cd rust
cargo build
cargo test
cd ..

# 4. Set up Python
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dev dependencies
cd python
pip install -e ".[dev]"
cd ..

# 6. Verify everything
./target/debug/victory --version
python3 -m victory.engine < /dev/null
```

##  Project Structure

```
victory/
├── rust/                         # Rust CLI
│   ├── Cargo.toml               # Rust dependencies
│   ├── src/
│   │   ├── main.rs              # Entry point
│   │   ├── cli/mod.rs           # Subcommands
│   │   ├── ipc/mod.rs           # NDJSON protocol
│   │   ├── orchestrator/mod.rs  # Workflow
│   │   ├── ui/mod.rs            # Terminal UI
│   │   └── config/mod.rs        # Config loading
│   └── target/                  # Build output
│
├── python/                       # Python engine
│   ├── setup.py                 # Python package config
│   ├── victory/
│   │   ├── __init__.py
│   │   ├── engine.py            # Main loop
│   │   ├── core/
│   │   │   ├── llm/             # LLM providers
│   │   │   ├── patcher/         # Patching logic
│   │   │   ├── executor/        # Test execution
│   │   │   ├── agent/           # Agent loop
│   │   │   ├── github/          # GitHub API
│   │   │   ├── token_manager/   # Cost tracking
│   │   │   └── setup.py         # Configuration
│   │   └── plugins/             # Language plugins
│   └── tests/                   # Python tests
│
├── docs/                         # Documentation ( New!)
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── USER_GUIDE.md
│   ├── EXAMPLES.md
│   ├── ARCHITECTURE.md
│   ├── IPC_PROTOCOL.md
│   ├── DESIGN_DECISIONS.md
│   ├── MODULES.md
│   ├── DEVELOPMENT.md            # This file
│   ├── CONTRIBUTING.md
│   ├── PLUGINS.md
│   ├── LLM_INTEGRATION.md
│   ├── PERFORMANCE.md
│   ├── SECURITY.md
│   ├── TROUBLESHOOTING.md
│   └── ROADMAP.md
│
└── test_*.py                     # Integration tests
```

##  Development Workflow

### Rust Development

**Build & Test:**
```bash
cd rust
cargo build               # Debug binary
cargo build --release    # Optimized binary
cargo test              # Run tests
cargo check             # Quick type check
```

**Code Quality:**
```bash
cargo fmt               # Format code
cargo clippy            # Linting
cargo doc --open        # Documentation
```

**Debug Logging:**
```bash
RUST_LOG=debug cargo run -- plan 1
RUST_LOG=victory=trace cargo run -- plan 1  # Module-specific
```

### Python Development

**Activate Environment:**
```bash
source venv/bin/activate
cd python
```

**Install & Test:**
```bash
pip install -e .         # Editable install (dev mode)
pip install -e ".[dev]"  # With dev dependencies
pytest -v               # Run tests with verbose
pytest --cov            # Generate coverage report
```

**Code Quality:**
```bash
black .                 # Format code
black --check .         # Check without formatting
mypy .                  # Type checking
pylint victory/         # Linting
```

**Manual Testing:**
```bash
# Test engine directly
python3 -m victory.engine

# Test specific module
python3 -c "from victory.core.llm import ModelDiscovery; print('Import OK')"

# Run single test
pytest tests/test_llm.py::test_discover_models -v
```

## 🔨 Making Changes

### Adding a New Command

**Step 1**: Add Rust side (`rust/src/cli/mod.rs`)
```rust
pub async fn handle_new_command(args: <Args>) -> Result<()> {
    let request = json!({
        "command": "new_command",
        "args": args
    });
    // Send request to Python...
}
```

**Step 2**: Add Python side (`python/victory/engine.py`)
```python
async def on_new_command(data):
    # Handle the command
    result = await process_command(data)
    return {"status": "success", "result": result}
```

**Step 3**: Test
```bash
./target/debug/victory new-command --args
```

### Adding a New LLM Provider

**Step 1**: Create provider file (`python/victory/core/llm/kimi.py`)
```python
from .base import BaseLLMProvider

class KimiProvider(BaseLLMProvider):
    async def plan(self, issue_desc: str) -> str:
        # Implementation
        pass
```

**Step 2**: Register in factory (`python/victory/core/llm/__init__.py`)
```python
from .kimi import KimiProvider
LLMProviderFactory.register("kimi", KimiProvider)
```

**Step 3**: Test
```python
provider = LLMProviderFactory.create("kimi", api_key, "model")
result = await provider.plan("Test issue")
```

### Adding Plugin Support

**Step 1**: Create plugin (`python/victory/plugins/go/executor.py`)
```python
class GoTestExecutor:
    async def run(self, path: str) -> TestSuiteResult:
        # Run go test ./...
        pass
```

**Step 2**: Register in detector (`python/victory/core/executor/executor.py`)
```python
async def detect_framework(self):
    if Path("go.mod").exists():
        return "go"
```

**Step 3**: Test
```python
executor = TestExecutor("/go-repo")
framework = await executor.detect_framework()  # Should be "go"
```

##  Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_llm.py -v

# Specific test
pytest tests/test_llm.py::test_discover_models -v

# With coverage
pytest tests/ --cov=victory --cov-report=html

# Watch mode (needs pytest-watch)
ptw tests/
```

### Integration Tests

```bash
# Full CLI test
python3 test_victory_cli.py

# Phase 2 integration test
python3 test_phase2_integration.py

# End-to-end
./target/debug/victory plan 1
```

### Writing Tests

**Python test example:**
```python
import pytest
from victory.core.llm import ModelDiscovery

@pytest.mark.asyncio
async def test_discover_openai_models():
    """Test fetching OpenAI models"""
    models = await ModelDiscovery._get_openai_fallback()
    assert len(models) > 0
    assert any("gpt-" in m.name for m in models)
```

## 🔧 Debugging Tips

### Enable Detailed Logging

**Rust:**
```bash
RUST_LOG=debug ./target/debug/victory -v plan 1
```

**Python:**
```bash
python3 -m victory.engine  # Logs go to stderr automatically
```

### Inspect NDJSON Protocol

**See what Rust sends:**
```bash
strace -e write ./target/debug/victory plan 1 2>&1 | grep '"command"'
```

**See what Python receives/sends:**
```bash
python3 -c '
import sys, json
for line in sys.stdin:
    msg = json.loads(line)
    print("Received:", json.dumps(msg, indent=2))
' <<< '{"command":"plan","issue_id":1}'
```

### Test Python Engine Directly

```bash
(
  echo '{"command":"plan","issue_id":1}'
  sleep 0.5
  echo '{"command":"plan","issue_id":2}'
) | python3 -m victory.engine
```

### Breakpoint Debugging

**Python:**
```python
import pdb; pdb.set_trace()  # Stop here
```

**Rust:**
```rust
dbg!(variable);  // Print variable
```

##  Running Specific Scenarios

### Test LLM Discovery

```bash
python3 << 'EOF'
import asyncio
from victory.core.llm import ModelDiscovery

async def test():
    models = await ModelDiscovery.discover_all("openai", "sk-test")
    for m in models:
        print(f"{m.name}: {m.display_name}")

asyncio.run(test())
EOF
```

### Test Patching

```bash
python3 << 'EOF'
import asyncio
import tempfile
from pathlib import Path
from victory.core.patcher import CodePatcher

async def test():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("print('hello')")
        
        # Apply patch
        patcher = CodePatcher(tmpdir)
        patch = """--- a/test.py
+++ b/test.py
@@ -1 +1 @@
-print('hello')
+print('world')
"""
        result = await patcher.apply_patch(patch)
        print("Result:", result)
        print("Content:", test_file.read_text())

asyncio.run(test())
EOF
```

### Test Agent Loop

```bash
python3 << 'EOF'
import asyncio
from victory.core.agent import AgentLoop

async def test():
    loop = AgentLoop("modal", "test-key", "/repo")
    await loop.initialize("zai-org/GLM-5.1-FP8")
    result = await loop.run(42, "Fix the bug")
    print(result)

asyncio.run(test())
EOF
```

##  Code Style Guidelines

### Python

```python
# Type hints on all functions
def process_data(value: str) -> Dict[str, Any]:
    """Detailed docstring.
    
    Args:
        value: Description
        
    Returns:
        Description
        
    Raises:
        ValueError: When...
    """
    pass

# Use f-strings
message = f"Processing {value}"

# Use type hints in class
from typing import Optional

class MyClass:
    value: Optional[str] = None
```

### Rust

```rust
/// Document public APIs
/// 
/// # Errors
/// Returns error if...
pub async fn process() -> Result<()> {
    Ok(())
}

// Use meaningful variable names
let is_valid = check_validity();

// Comments for non-obvious logic
// This happens because of X (see issue #123)
```

##  Committing Code

### Conventional Commits

Format:
```
<type>(<scope>): <subject>

<body>

Fixes #<issue>
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code restructuring
- `perf` - Performance improvement
- `test` - Test additions
- `chore` - Build, dependencies

Examples:
```
feat(llm): add Kimi provider support
fix(patcher): handle multi-file diffs correctly
docs: update LLM integration guide
refactor(agent): simplify iteration logic
perf: optimize token counting
test: add test cases for edge cases
```

### Pre-commit Checklist

- [ ] Code passes `cargo fmt` and `black`
- [ ] Tests pass locally
- [ ] No new warnings from `cargo clippy`
- [ ] Python types check with `mypy`
- [ ] Updated docs if needed
- [ ] Commit message follows conventions

##  Release Process

### Version Bumping

```bash
# Update version in Cargo.toml and setup.py
# Tag release
git tag v0.2.0
git push origin v0.2.0
```

###Build Release Binary

```bash
cd rust
cargo build --release
# Binary at: target/release/victory
```

##  Common Issues

### "Cargo not found"
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### "Python import error"
```bash
# Reinstall
cd python
pip uninstall victory
pip install -e .
```

### "Test failures"
```bash
# Run with verbose traceback
pytest tests/ -v -s --tb=long
```

##  Contributing Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and commit with conventional commits
4. Run tests: `pytest && cargo test`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request
7. Address review feedback
8. Merge when approved

---

**Need Help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or ask in discussions.
