# ⚡ Victory

AI-powered CLI tool for open source contributors.

## 🎯 Vision

Victory is a production-grade CLI tool that leverages AI to help open source contributors:

- Understand any codebase (multi-language via plugins)
- Fetch and analyze GitHub issues
- Plan how to fix issues
- Automatically generate code patches
- Apply patches locally and run tests
- Iterate until issues are resolved
- Analyze CI/CD failures
- Perform performance testing
- Visualize dependency graphs
- Support multiple LLM providers (OpenAI, Gemini, Claude, Kimi, MiniMax)

**Goal**: "Run one command → get a working PR"

## 🏗️ Architecture

Victory uses a **hybrid Rust + Python** architecture:

- **Rust CLI**: Performance-critical, system execution, binary distribution
- **Python Engine**: AI intelligence, LLM integration, complex analysis

### Communication

Components communicate via **NDJSON** (newline-delimited JSON) over stdin/stdout:

```
Rust CLI
   ↓
   └─→ stdin  → Python Engine
   ↑
   └─← stdout ← Python Engine
```

## 📦 Project Structure

```
victory/
├── rust/                          # Rust CLI
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs               # Entry point
│       ├── cli/                  # CLI commands
│       ├── ipc/                  # NDJSON IPC module
│       ├── orchestrator/         # Orchestrates Rust-Python flow
│       ├── ui/                   # Colored output
│       ├── config/               # Configuration
│       ├── git/                  # Git operations (stub)
│       ├── parser/               # Code parsing (stub)
│       └── graph/                # Dependency graphs (stub)
│
├── python/                        # Python Engine
│   ├── setup.py
│   └── victory/
│       ├── __init__.py
│       ├── engine.py             # Main NDJSON listener
│       └── core/
│           ├── agent/            # AI Agent loop (stub)
│           ├── llm/              # LLM integrations (stub)
│           ├── token_manager/    # Token tracking (stub)
│           ├── github/           # GitHub API (stub)
│           ├── planner/          # Issue planner (stub)
│           └── patcher/          # Code patcher (stub)
│       └── plugins/
│           ├── python/           # Python language support
│           └── typescript/       # TypeScript language support
│
└── docs/
    ├── ARCHITECTURE.md
    ├── IPC_PROTOCOL.md
    └── CLI_GUIDE.md
```

## 🚀 Getting Started

### Prerequisites

- Rust 1.70+ (with Cargo)
- Python 3.9+
- Git

### Installation

1. Clone and navigate:
```bash
cd victory
```

2. Build Rust CLI:
```bash
cd rust
cargo build --release
cd ..
```

3. Setup Python environment:
```bash
python3 -m venv venv
source venv/bin/activate
cd python
pip install -e .
cd ..
```

### Running Victory

```bash
# Plan how to fix issue #1
./target/debug/victory plan 1

# Full agent loop on issue #123
./target/debug/victory issue 123

# Apply an existing plan
./target/debug/victory apply my-plan
```

### Verbose Logging

```bash
./target/debug/victory -v plan 1
```

## 📋 NDJSON Protocol

### Request (Rust → Python)

```json
{
  "command": "plan|issue|apply|test_results",
  "issue_id": 123,
  "repo_path": "/project",
  "iteration": 1
}
```

### Response (Python → Rust)

```json
{
  "status": "success|pending|error",
  "action": "apply_patch|run_tests|continue|stop",
  "message": "Human-readable message",
  "patch": "unified diff (optional)",
  "logs": "Debug logs (optional)",
  "token_usage": {
    "used": 1000,
    "max": 4000,
    "cost": 0.05
  }
}
```

### Callback (Rust → Python)

```json
{
  "command": "test_results",
  "test_status": "passed|failed",
  "test_logs": "Test output"
}
```

## 🧵 Process Management

- Rust spawns Python subprocess
- Python stays alive (persistent loop)
- Rust detects 30-second timeouts
- Auto-restart on failure with 1 retry
- Graceful shutdown on error

## 🎨 CLI Output

```
[i] Info message          → Blue
[✓] Success message       → Green
[✗] Error message         → Red
[!] Warning message       → Yellow
```

## 🗂️ Stdout/Stderr Rules

- **Python stdout**: ONLY NDJSON messages (one JSON object per line)
- **Python stderr**: Logs, debug info, print statements
- **Rust**: Parses stdout, pipes stderr to CLI logs

## 🔒 Execution Model

- **Python**: NO system command execution
- **Python**: Request via NDJSON (`"action": "run_tests"`)
- **Rust**: Execute all system commands (pytest, jest, git, etc.)

## 📚 Current Status

Currently implemented:
- ✅ Rust CLI with subcommands (plan, issue, apply)
- ✅ NDJSON IPC communication
- ✅ Process spawning and management
- ✅ Python engine stub
- ✅ `victory plan 1` command (working end-to-end)

To be implemented:
- LLM integration
- Git operations
- Code parsing and analysis
- Full agent loop
- Patch generation and testing
- Token management
- GitHub integration

## 🧪 Testing

```bash
# Test end-to-end
./target/debug/victory plan 1

# Test Python engine directly
echo '{"command":"plan","issue_id":1}' | python3 -m victory.engine
```

## 📖 More Documentation

- [Architecture Details](docs/ARCHITECTURE.md)
- [IPC Protocol Spec](docs/IPC_PROTOCOL.md)

## 🤝 Contributing

Victory welcomes contributions! See the [Contributing Guidelines](CONTRIBUTING.md).

## 📄 License

Victory is open source. See LICENSE file for details.

## 🎯 Roadmap

- [x] Phase 1: Core CLI and IPC
- [ ] Phase 2: LLM integration
- [ ] Phase 3: GitHub issue fetching
- [ ] Phase 4: Code analysis and patching
- [ ] Phase 5: Multi-language support
- [ ] Phase 6: Performance and stress testing
- [ ] Phase 7: CI/CD failure analysis
- [ ] Phase 8: Production release

Visualize your dependency graph:
```bash
victory graph
```

## 🔐 Safety

- Max 5 iterations per issue.
- Sandboxed execution (Python delegates all system changes to Rust).
- Conventional Commit standards enforced.
