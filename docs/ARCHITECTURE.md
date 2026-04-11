# Architecture

Victory's system design and component overview.

##  High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Victory CLI                            │
│                  (Node.js - Entry Point)                    │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Command Dispatcher (--init, --config, issue, plan)    │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ UI Layer (Premium Blue Theme, ANSI styling)            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ IPC Manager (Process orchestration, NDJSON)            │ │
│  └────────────────────────────────────────────────────────┘ │
│                      │                                       │
│                      │ NDJSON (stdin/stdout)               │
│                      ▼                                       │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ Persistent Child Process
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Victory Engine                            │
│                  (Python - AI Core)                          │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Agent Loop (Plan → Patch → Apply → Test → Iterate)    │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ LLM Adapters (Claude, OpenAI, Gemini, Modal, Kimi)     │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ GitHub Client (Issues, PRs, Comments)                  │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Code Patcher & Test Executor                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                      │                                       │
│                      │ NDJSON responses
│                      ▼                                       │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ (Optional / Planned)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Victory Hub                              │
│                  (Rust - High Perf)                          │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Fast FS Operations                                     │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Parallel Computation                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

##  Request-Response Flow

### 1. Plan Command

```
Command: victory plan 42
    ↓
[Rust] Parse args, spawn Python
    ↓
[Rust] Send NDJSON: {"command":"plan","issue_id":42}
    ↓
[Python] Receive command on stdin
    ↓
[Python] Dispatch to plan handler
    ↓
[Python] Call LLM to analyze issue
    ↓
[Python] Return NDJSON: {"status":"success","plan":"..."}
    ↓
[Rust] Parse response
    ↓
[Rust] Display: [✓] Plan generated for issue #42
    ↓
[Rust] Stop Python process
```

### 2. Full Issue Command

```
Command: victory issue 123
    ↓
[Rust] Spawn Python (stays alive)
    ↓
[Orchestrator] Step 1: PLAN
    ↓ LLM generates strategy
    ↓
[Orchestrator] Step 2: PATCH
    ↓ LLM generates unified diff
    ↓
[Orchestrator] Step 3: APPLY
    ↓ CodePatcher applies changes
    ↓
[Orchestrator] Step 4: TEST
    ↓ TestExecutor runs suite
    ↓
[Orchestrator] Evaluate results
    ├─ If pass → SUCCESS
    └─ If fail → ANALYZE & ITERATE (max 5x)
    ↓
[Rust] Display results
    ↓
[Rust] Optional: Create PR
```

##  Component Details

### Node.js CLI Layer (Entry Point)

**Responsibilities:**
- Global CLI entry point and argument parsing
- Interactive setup wizard and configuration management
- Premium UI rendering with ANSI blue theme
- Process orchestration and lifecycle management
- IPC message serialization/deserialization (NDJSON)

**Key Files:**
- `bin/victory` - Main script and command handlers
- `package.json` - Dependency and distribution management

**Why Node.js:**
- Rapid CLI development
- Excellent terminal styling ecosystem
- Native npm distribution for globality
- Asynchronous process management

### Python Engine Layer (AI Core)

**Responsibilities:**
- AI/LLM orchestration and decision making
- GitHub API integration (Issues, PRs)
- Strategic planning and code analysis
- Patch generation and iterative refinement
- Multi-framework test execution and failure analysis

**Key Modules:**
- `engine.py` - Core listener and command dispatcher
- `victory/core/agent/` - Agent loop and logic
- `victory/core/llm/` - Multi-provider LLM adapters
- `victory/core/github/` - Repository integration

### Rust Hub Layer (High Performance)

**Responsibilities:**
- High-performance filesystem operations
- Parallel computation and binary utilities
- System-level optimizations
- (Used as a support layer for intensive tasks)

**Key Modules:**
- `rust/src/orchestrator/` - High-speed workflow units
- `rust/src/ui/` - Fast terminal rendering components

### NDJSON Protocol

**Design Principle:** One JSON object per line

```
Message Format:
  [JSON object]
  \n
  [JSON object]
  \n

Example:
  {"command":"plan","issue_id":1}
  \n
  {"status":"success","plan":"..."}
  \n
```

**Advantages:**
- Human-readable (debuggable)
- No complex parsing
- Streaming-friendly
- Natural line-buffering
- Works with standard Unix tools

##  Plugin Architecture

### Language Support

Victory supports multiple programming languages via plugins:

```
python/
├── plugins/
│   ├── python/
│   │   ├── __init__.py
│   │   ├── parser.py      # AST parsing
│   │   ├── executor.py    # pytest runner
│   │   └── formatter.py   # black/autopep8
│   ├── typescript/
│   │   ├── __init__.py
│   │   ├── parser.ts      # TypeScript-specific
│   │   ├── executor.ts    # Jest runner
│   │   └── formatter.ts   # Prettier
│   └── rust/
│       ├── __init__.py
│       ├── parser.rs
│       └── executor.rs    # cargo test
```

### Extension Points

Plugins can extend:
1. **Execution**: Custom test runners
2. **Parsing**: Language-specific code analysis
3. **Formatting**: Code style enforcement
4. **Validation**: Pre/post-fix checks

##  Safety & Reliability

### Automatic Backups

Before modifying files:
```
~/.victory/backups/
├── file_1_2026-04-10T09-35-42.bak
├── file_2_2026-04-10T09-35-42.bak
└── file_3_2026-04-10T09-35-42.bak
```

### Rollback on Failure

If tests fail:
1. Keep current state (for analysis)
2. Create comparison with backup
3. Allow human review
4. Optionally rollback to backup

### Timeout Detection

```
30-second timeout triggers:
  1. Kill Python process
  2. Log error
  3. Auto-restart (with cooldown)
  4. Mark as failed
```

### Token Budget

```
Track spending:
  OpenAI: $5.00/hr limit
  Gemini: $1.00/hr limit
  Claude: $3.00/hr limit

When limit reached:
  - Stop accepting new commands
  - Warn user
  - Save current state
```

##  Data Flow Diagram

### Simple Fix (Successful Path)

```
Issue
  │
  └─→ LLM Plan
      │
      └─→ Generate Patch
          │
          └─→ Apply Patch
              │
              └─→ Run Tests
                  │
                  └─→ ✅ All Pass
                      │
                      └─→ Create PR
                          │
                          └─→ Done
```

### Complex Fix (With Iteration)

```
Issue
  │
  └─→ LLM Plan (Attempt 1)
      │
      └─→ Patch & Test
          │
          ├─→ ❌ Test Fails
          │   │
          │   └─→ Analyze Failure (Attempt 2)
          │       │
          │       └─→ New Plan
          │           │
          │           └─→ New Patch & Test
          │               │
          │               ├─→ ❌ Test Fails (Attempt 3)
          │               │   │
          │               │   └─→ [Loop back...]
          │               │
          │               └─→ ✅ Test Passes
          │                   │
          │                   └─→ Done
          │
          └─→ ✅ Test Passes (First Try)
              │
              └─→ Done
```

##  Configuration Hierarchy

### Precedence (highest to lowest)

1. **Command-line flags**
   ```bash
   victory issue 42 --llm openai --max-iterations 8
   ```

2. **Environment variables**
   ```bash
   VICTORY_LLM=openai VICTORY_MAX_ITERATIONS=8
   ```

3. **Config file** (~/.victory/config.yaml)
   ```yaml
   llm: openai
   max-iterations: 8
   ```

4. **Built-in defaults**
   ```
   llm: modal
   max-iterations: 5
   ```

##  Design Decisions

### Why Persistent Python Process?

**Alternative**: Spawn new Python for each command
- ✅ Less memory
- ❌ Cold start overhead (2-3 seconds per command)
- ❌ Can't share state between commands

**Our Approach**: Single persistent process
- ✅ Near-instant response
- ✅ Shared state (cache, connections)
- ✅ Better for interactive workflows

### Why NDJSON not Protocol Buffers?

**Alternative**: Binary protocol (protobuf)
- ✅ Smaller message size
- ✅ Faster serialization
- ❌ Not human-readable
- ❌ Harder to debug

**Our Approach**: NDJSON (text-based JSON)
- ✅ Human-readable
- ✅ Easy debugging
- ✅ Language-agnostic
- ✓ Acceptable performance

### Why Hybrid Rust+Python?

**Alternative 1**: Pure Rust
- ✅ Single binary
- ✅ No runtime needed
- ❌ LLM ecosystem is Python-focused
- ❌ Slower development iteration

**Alternative 2**: Pure Python
- ✅ Single ecosystem
- ✅ Easier to extend
- ❌ No binary distribution
- ❌ Startup overhead

**Our Approach**: Hybrid
- ✅ Best of both worlds
- ✅ Rust for performance, Python for flexibility
- ✅ Clear separation of concerns

##  Extension Points

Future capabilities can be added at these points:

1. **New LLM Providers**: Add to `llm/providers/`
2. **New Commands**: Add to `cli/` and handlers
3. **Custom Plugins**: Language support in `plugins/`
4. **Pre/Post Hooks**: Extensible hook system
5. **Custom Prompts**: Override in `~/.victory/prompts/`

##  Performance Targets

- **Startup**: < 2 seconds
- **Command response**: < 100ms (p95)
- **Issue planning**: < 30 seconds
- **Full automation**: < 5 minutes (for simple issues)
- **Token rate**: < 1000 tokens/minute

##  Security Considerations

- Config files: 0600 permissions (user-readable only)
- API keys: Never logged or exposed
- Code execution: Sandboxed to repository
- File operations: Restricted to repository + backups
- Network: Only to authorized (GitHub, LLM APIs)

---

**See Also:**
- [IPC_PROTOCOL.md](IPC_PROTOCOL.md) - Detailed protocol spec
- [MODULES.md](MODULES.md) - Component documentation
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) - Design rationale
