# Quick Start Guide

## Installation

### Option 1: Automated Setup

```bash
bash install.sh
```

### Option 2: Manual Setup

**Prerequisites:**
- Rust 1.70+ (install from https://rustup.rs)
- Python 3.9+
- Git

**Build:**
```bash
# Build Rust CLI
cd rust
cargo build --release
cd ..

# Setup Python
python3 -m venv venv
source venv/bin/activate

cd python
pip install -e .
cd ..

# Add to PATH
export PATH=$PATH:$PWD/target/release
```

## First Steps

### 1. View Help

```bash
./target/debug/victory --help
```

Output:
```
AI-powered CLI tool for open source contributors

Usage: victory [OPTIONS] <COMMAND>

Commands:
  plan   Plan how to fix an issue
  issue  Run full agent loop on an issue
  apply  Apply an existing plan
  help   Print this message or the subcommand(s)

Options:
  -v, --verbose          Verbose logging
  -c, --config <CONFIG>  Configuration file path
  -h, --help             Print help
  -V, --version          Print version
```

### 2. Test the CLI (Stub Version)

Plan an issue (shows stub response):

```bash
./target/debug/victory plan 1
```

Expected output:
```
[i] Planning fix for issue #1
[✓] Plan generated for issue #1
```

With verbose logging:

```bash
./target/debug/victory -v plan 1
```

This shows:
- [i] Planning fix for issue #1
- Timestamp logs from Rust and Python
- [✓] Plan generated for issue #1

### 3. Run Direct Python Engine Test

```bash
source venv/bin/activate
echo '{"command":"plan","issue_id":1}' | python3 -m victory.engine
```

Expected output (on stdout):
```
{"status": "success", "action": "stop", "message": "Plan generated for issue #1"}
```

Debug output (on stderr):
```
2026-04-10 09:36:35,232 [INFO] __main__: Victory Python Engine started
2026-04-10 09:36:35,232 [DEBUG] __main__: Command received: {...}
```

## Architecture Overview

**Component Flow:**
```
User runs: victory plan 1
    ↓
Rust CLI (main.rs)
    ↓
Spawns: python -m victory.engine (subprocess)
    ↓
Sends NDJSON: {"command":"plan","issue_id":1}
    ↓
Python engine receives on stdin
    ↓
Processes command
    ↓
Sends NDJSON response on stdout
    ↓
Rust parses response
    ↓
Displays colored output
    ↓
Stops Python subprocess
```

## Key Files

- **rust/src/main.rs** - Rust CLI entry point
- **rust/src/ipc/mod.rs** - NDJSON communication protocol
- **python/victory/engine.py** - Python engine main loop
- **docs/ARCHITECTURE.md** - System design details
- **docs/IPC_PROTOCOL.md** - Protocol specification

## Development

### Rust Development

```bash
cd rust
cargo build          # Debug build
cargo build --release  # Optimized build
cargo test           # Run tests
cargo check          # Quick check without building
cargo fmt            # Format code
cargo clippy         # Lint
```

### Python Development

```bash
source venv/bin/activate
cd python
pip install -e .     # Editable install
python -m victory.engine  # Run engine directly
python -m pytest     # Run tests
black .              # Format code
```

### Running End-to-End

```bash
# Terminal 1: Watch Rust/Python communication
RUST_LOG=debug ./target/debug/victory -v plan 1

# Terminal 2: Only see Python output
./venv/bin/python -c "import sys; print('test')" 2>&1 | grep -v "DEBUG"
```

## Debugging

### Enable All Logging

```bash
RUST_LOG=debug,victory=debug ./target/debug/victory -v plan 1 2>&1
```

### Test Python Engine Directly

```bash
# Multiple commands
(
  echo '{"command":"plan","issue_id":1}'
  sleep 0.5
  echo '{"command":"plan","issue_id":2}'
) | python3 -m victory.engine
```

### Check Process Communication

```bash
# Start CLI with strace to see subprocess calls
strace -e trace=execve ./target/debug/victory plan 1

# Watch stdin/stdout
strace -e trace=write ./target/debug/victory plan 1
```

## Common Issues

### "Python process closed the connection"

- Python engine crashed or exited unexpectedly
- Check stderr output for Python errors
- Run with `-v` flag for verbose logging

### "Process timeout (30s)"

- Python engine hung on LLM call
- Check network connectivity
- Verify API keys are set (future)

### "Command not found: victory"

- Add to PATH: `export PATH=$PATH:$PWD/target/release`
- Or use absolute path: `./target/debug/victory plan 1`

## Next Steps

1. **Explore the code:**
   - `rust/src/cli/mod.rs` - CLI commands
   - `rust/src/orchestrator/mod.rs` - Command coordination
   - `python/victory/engine.py` - Engine loop

2. **Read documentation:**
   - [ARCHITECTURE.md](../docs/ARCHITECTURE.md)
   - [IPC_PROTOCOL.md](../docs/IPC_PROTOCOL.md)

3. **Start implementing:**
   - Add LLM integration to `python/victory/core/llm/`
   - Add GitHub integration to `python/victory/core/github/`
   - Implement agent loop in `python/victory/core/agent/`

## Support

For issues or questions:
1. Check the documentation
2. Review the code comments
3. Search existing issues
4. Create a new issue with details
