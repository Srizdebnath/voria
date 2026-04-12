# Design Decisions

Rationale behind voria's key architectural and technical choices.

##  Core Decisions

### 1. Hybrid Rust + Python Architecture

**Decision**: Use Rust for CLI and Python for engine.

**Rationale**:
- **Rust**: High performance, compiled binary, async I/O, type-safe system operations
- **Python**: Rich LLM ecosystem, fast development, extensive libraries

**Alternatives Considered**:
- ❌ Pure Rust: Missing LLM ecosystem, slower iteration
- ❌ Pure Python:  No binary distribution, slow startup
- ✅ Hybrid: Best of both worlds

**Trade-offs**:
- ✅ Docker/pipeline distribution easier with binary
- ❌ Requires two build toolchains
- ✅ Clear separation simplifies testing

### 2. NDJSON Inter-Process Communication

**Decision**: Use newline-delimited JSON over stdin/stdout.

**Rationale**:
- Human-readable (debuggable with echo/cat)
- Language-agnostic
- Natural streaming behavior
- No special serialization library needed

**Alternatives Considered**:
- ❌ Protocol Buffers: Fast but binary (hard to debug)
- ❌ gRPC: Overkill for single-machine communication
- ❌ Unix sockets: Platform-specific
- ✅ NDJSON: Simplicity + debuggability

**Trade-offs**:
- ✅ Easy to debug (just inspect messages)
- ❌ Slightly larger message size
- ✅ Minimal parsing overhead

### 3. Persistent Python Process

**Decision**: Keep Python engine alive between commands.

**Rationale**:
- Instant response times
- Shared state (caches, connections)
- Better for interactive workflows

**Alternatives Considered**:
- ❌ Fresh process per command: Simpler but 2-3sec overhead
- ✓ Persistent process: Better UX

**Trade-offs**:
- ✅ Fast response
- ❌ More memory usage
- ✅ Better for scripting

### 4. Iterative Agent Loop (5 iterations max)

**Decision**: Retry fix up to 5 times if tests fail.

**Rationale**:
- Handles complex fixes that need refinement
- Learns from test failures
- Bounded (prevents infinite loops)

**Why 5?**:
- 1-2 iterations: 80% issues fixed
- 3-5 iterations: Handle complex cases
- 6+: Diminishing returns, too costly

**Trade-offs**:
- ✅ Better fix success rate
- ❌ Higher LLM token usage
- ✅ Bounded costs (5 iterations max)

### 5. Automatic Backup and Rollback

**Decision**: Create backups before modifying files, rollback on failure.

**Rationale**:
- Safety: Recover from bad patches
- Debugging: Compare before/after
- Confidence: Users can experiment

**Trade-offs**:
- ✅ Very safe
- ❌ Disk space for backups
- ✅ File recovery support

### 6. Token Budget Enforcement

**Decision**: Track & enforce spending limits per provider.

**Rationale**:
- Prevent runaway costs (important with LLMs!)
- Per-provider budgets (different pricing models)
- User control over spending

**Implementation**:
```
Modal:   $0.00/hr (free until Apr 30)
OpenAI:  $5.00/hr
Gemini:  $1.00/hr
Claude:  $3.00/hr
```

**Trade-offs**:
- ✅ Prevents bill shock
- ❌ May stop mid-operation
- ✅ User can increase budget

##  LLM Integration Decisions

### 1. Multi-Provider Support (4 maximum)

**Decision**: Support Modal, OpenAI, Google Gemini, and Anthropic Claude.

**Rationale**:
- **Modal**: Free until Apr 30, great for testing
- **OpenAI**: Industry standard, reliable
- **Gemini**: Fast and cost-effective
- **Claude**: Highest quality (when budget allows)

**Why exactly 4?**:
- Too few: Limited options
- Too many: Maintenance burden
- 4 is sweet spot

**Trade-offs**:
- ✅ Good coverage
- ✅ User choice
- ❌ More integration code

### 2. Dynamic Model Discovery

**Decision**: Fetch available models from provider APIs at runtime.

**Rationale**:
- NO hardcoding (breaks when providers add new models)
- Users can choose from latest models
- Automatic fallback if API unavailable

**Trade-offs**:
- ✅ Always up-to-date
- ❌ Extra API calls on setup
- ✅ User empowerment

### 3. Interactive Setup over CLI Flags

**Decision**: `python3 -m voria.core.setup` for configuration.

**Rationale**:
- Better UX (guided steps)
- Less memorization needed
- Validation at setup time

**Trade-offs**:
- ✅ User-friendly
- ❌ Doesn't work in scripts
- ✓ Env vars available for scripting

##  Code Organization Decisions

### 1. Module Structure

**Decision**: Organize by functionality (llm/, agent/, patcher/) not by feature.

**Rationale**:
- Clear separation of concerns
- Easy to test modules independently
- Simple to extend (add new providers)

**Alternative** (rejected):
```
# ❌ Feature-based
voria/
├── github_automation/
│   ├── llm.py
│   ├── patcher.py
│   └── tests.py
├── code_analysis/
│   ├── llm.py
│   └── patcher.py
```

**Our Structure** (accepted):
```
# ✅ Responsibility-based
voria/
├── core/
│   ├── llm/          (all LLM logic)
│   ├── patcher/      (all patching)
│   ├── agent/        (orchestration)
│   └── github/       (GitHub API)
```

### 2. Async/Await Everywhere

**Decision**: Use async I/O throughout (no blocking operations).

**Rationale**:
- Better resource utilization
- Handle multiple operations simultan eously
- Responsive CLI

**Trade-offs**:
- ✅ Efficient I/O
- ❌ More complex code
- ✅ Future-proof for concurrency

### 3. Configuration over Hardcoding

**Decision**: All settings configurable (CLI flags, env vars, config files).

**Rationale**:
- Users customize behavior
- Easy A/B testing
- No recompilation needed

**Hierarchy** (highest to lowest priority):
1. CLI flags: `--llm openai`
2. Environment: `voria_LLM=openai`
3. Config file: `~/.voria/config.yaml`
4. Defaults: Built-in sensible defaults

##  Security Decisions

### 1. Config File Permissions

**Decision**: Store configs at `~/.voria/` with `0600` (user-only).

**Rationale**:
- API keys stored locally (not on server)
- Restricted permissions prevent accidental sharing
- Follows Unix best practices

### 2. Code Execution Sandboxing

**Decision**: Rust executes system commands, Python never does.

**Rationale**:
- Controlled execution environment
- Audit trail (which commands ran)
- Prevents Python malcode injection

**Trade-offs**:
- ✅ More secure
- ❌ Extra RPC calls
- ✅ Better failure handling

### 3. No Credentials in Logs

**Decision**: Never log API keys, tokens, or credentials.

**Rationale**:
- Prevent accidental exposure
- Safe to share logs for debugging
- Follows security best practices

##  UX Decisions

### 1. Colored Output with Unicode

**Decision**: Use colored terminal output + Unicode symbols.

**Rationale**:
- Easy to scan output
- Visual feedback (success/error)
- Modern CLI UX

**Symbols**:
- ✅ Success
- ❌ Error
- 🔄 In progress
- ℹ️ Info

### 2. Verbose Flag for Debugging

**Decision**: `-v/--verbose` enables detailed logging.

**Rationale**:
- Clean default output for users
- Detailed trace for debugging
- Toggleable without config changes

### 3. Dry-Run Testing

**Decision**: `--dry-run` flag simulates without modifications.

**Rationale**:
- Users can review changes before applying
- Testing without risk
- Confidence building

##  Performance Decisions

### 1. Timeout Detection (30 seconds)

**Decision**: Kill Python if no response for 30 seconds.

**Rationale**:
- Long enough for LLM calls
- Short enough for user feedback
- Prevents hangs

### 2. Auto-Retry on Failure

**Decision**: Retry once on timeout, then fail.

**Rationale**:
- Handles transient errors
- Don't retry forever (stuck)
- One retry is sweet spot

### 3. Lazy Loading

**Decision**: Load modules/data only when needed.

**Rationale**:
- Faster startup times
- Lower memory base
- Only pay for what you use

##  Testing Decisions

### 1. TArray of Test Frameworks Supported

**Decision**: Detect pytest, jest, go test (+ custom).

**Rationale**:
- Cover 90% of projects
- Custom command fallback
- Framework agnostic

**Why these 3?**:
- pytest: Python (most common)
- jest: JavaScript/TypeScript
- go test: Go (built-in)

### 2. Result Parsing

**Decision**: Parse framework output (not JSON APIs).

**Rationale**:
- No framework API dependency
- Works offline
- Resilient to version changes

##  Deployment Decisions

### 1. Single Binary Distribution

**Decision**: Distribute Rust binary only (Python downloaded automatically).

**Rationale**:
- Small binary (just Rust CLI)
- Python installed when first run
- Automatic dependency management

### 2. Docker Support Optional

**Decision**: Provide Dockerfile (not required for usage).

**Rationale**:
- Works on any system
- Dev/prod parity
- Advanced users can containerize

---

**See Also:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [MODULES.md](MODULES.md) - Component details
