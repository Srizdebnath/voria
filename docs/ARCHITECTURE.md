# Architecture Documentation

## System Overview

Victory follows a **hybrid Rust + Python** architecture designed for performance, maintainability, and scalability.

```
Rust CLI (Performance)  ←→  Python Engine (Intelligence)
    main.rs                    engine.py
    cli/                       core/
    ipc/                       plugins/
    orchestrator/
```

## Component Design

### Rust CLI Layer

**Purpose**: Command-line interface, process management, system integration

**Key Modules**:

- **main.rs**: Entry point, argument parsing, logging setup
- **cli/mod.rs**: Subcommand dispatch (plan, issue, apply)
- **orchestrator/mod.rs**: Orchestrates Rust-Python communication
- **ipc/mod.rs**: NDJSON protocol implementation, process management
- **config/mod.rs**: Configuration loading
- **ui/mod.rs**: Colored terminal output (Blue/Green/Red)

**Responsibility**:
- ✅ Execute system commands (git, pytest, npm, etc.)
- ✅ File I/O and manipulation
- ✅ Process spawning and management
- ✅ UI rendering with colors

### Python Engine Layer

**Purpose**: AI intelligence, LLM integration, complex analysis

**Key Modules**:

- **engine.py**: Main NDJSON listener and dispatcher
- **core/agent/**: AI agent loop implementation
- **core/llm/**: LLM provider integrations
- **core/planner/**: Issue analysis and planning
- **core/patcher/**: Code patch generation
- **core/github/**: GitHub API integration
- **core/token_manager/**: Token usage tracking
- **plugins/**: Language-specific support

**Responsibility**:
- ✅ Read NDJSON from stdin
- ✅ Parse and analyze code/issues
- ✅ Call LLM APIs
- ✅ Generate patches algorithmically
- ✅ Log debug info to stderr
- ❌ NO system command execution
- ❌ NO direct file writes (except via Rust)

---

## 🔗 IPC Protocol (NDJSON)

### Format Rules

1. **One JSON object per line** (exactly - no wrapping)
2. **No multi-line JSON** in protocol messages
3. **Always flush** after write (`sys.stdout.flush()`)
4. **Line-by-line reading** on both sides

### Stdout vs Stderr Rule

- **Python `stdout`:** EXCLUSIVELY NDJSON protocol messages (one JSON per line)
- **Python `stderr`:** All logs, debug info, print statements, error traces
- **Rust:** Parse stdout only; pipe stderr to console

This separation ensures debug output cannot corrupt the protocol.

---

## ⏱ Process Management

Rust spawns and manages the Python subprocess:

**Lifecycle**:
1. Rust calls `python -m victory.engine`
2. Python process stays alive (persistent loop)
3. Rust sends NDJSON requests via stdin
4. Python sends NDJSON responses via stdout
5. If no response for 30 seconds → timeout detection
6. Rust kills Python and restarts (retries once)
7. On CLI exit → graceful process termination

**Timeout Detection**:
- Monitor thread detects when 30 seconds pass without response
- Kills Python subprocess immediately
- Retries last request one time
- Exits with error if retry fails

---

---

## 🔄 Agent Lifecycle (The Loop)

Victory operates in a loop capped at **5 iterations**:
1. **Plan:** LLM analyzes files and issue description to create an implementation strategy.
2. **Patch:** LLM generates a Unified Diff.
3. **Execute:** Rust applies the patch to the local filesystem.
4. **Test:** Rust executes the project's test suite (e.g., `pytest`, `jest`).
5. **Analyze:** results are fed back to Python. If tests fail, the agent refines the plan and repeats.
6. **Finalize:** Upon success, Rust handles the final commit and push.

---

## 🔗 JSON Communication Contract

### Request (Rust → Python)
```json
{
  "command": "issue | plan | apply | graph",
  "issue_id": 123,
  "repo_path": "/path/to/repo",
  "iteration": 1,
  "context": {
    "files": [],
    "dependencies": {},
    "ci_logs": ""
  },
  "config": {
    "llm_provider": "gemini",
    "api_keys_present": true
  }
}
```

### Response (Python → Rust)
```json
{
  "status": "success | error | pending",
  "action": "run_tests | apply_patch | continue | stop",
  "message": "Reasoning string",
  "patch": "diff data...",
  "logs": "Detailed agent logs",
  "token_usage": {
    "used": 1000,
    "max": 128000,
    "cost": 0.01
  }
}
```

---

## 🎨 UI & Aesthetics

- **Primary Theme:** Blue-themed UI (using Rich or Console libraries).
- **Color Palette:**
  - Primary: Blue
  - Headers: Bright Blue
  - Success: Green
  - Errors: Red
  - Warnings: Yellow
- **Feedback:** Real-time token usage and cost visualization.

---

## 📦 Build & Distribution

- **Rust:** Managed by `cargo`.
- **Python:** Managed by `poetry`.
- **Linkage:** An `install.sh` script will:
  1. Build the Rust binary.
  2. Initialize the Python virtual environment and install dependencies.
  3. Link the `victory` binary to the system PATH.
- **Detection:** Rust will auto-detect the `.venv` directory for executing the Python engine.

---

## 🧪 Safety & Standards

- **Conventional Commits:** All automatic commits must follow standard conventions (e.g., `fix(scope): description`).
- **Atomic Operations:** Keep changes focused on the issue.
- **No Destruction:** Prevent destructive operations unless user-confirmed.
- **Context Limits:** Never exceed 60% of the LLM context window to maintain accuracy and prevent truncation errors.
