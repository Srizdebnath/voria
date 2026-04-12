# Module Documentation

Detailed documentation of voria's core modules and their APIs.

##  Python Core Modules

### `llm/` - LLM Provider Integration

**Purpose**: Abstract interface to multiple LLM providers.

**Key Classes**:
- `BaseLLMProvider` - Abstract base class
- `ModelDiscovery` - Runtime model discovery
- `ProviderSetup` - Interactive configuration
- `ModelInfo` - Model metadata
- Provider implementations:
  - `ModalProvider` - Modal Z.ai backend
  - `OpenAIProvider` - OpenAI API
  - `GeminiProvider` - Google Gemini  
  - `ClaudeProvider` - Anthropic Claude

**Main Methods**:
```python
# Discover available models
models = await LLMProviderFactory.discover_models("openai", api_key)

# Create provider instance
provider = LLMProviderFactory.create("openai", api_key, "gpt-5.4")

# Use provider
await provider.plan("Issue description")
await provider.generate_patch(issue_context, plan)
await provider.analyze_test_failure(test_output, code)
```

**Configuration**:
- Stored in `~/.voria/providers.json`
- Supports environment variable fallback
- Interactive setup via `python3 -m voria.core.setup`

**Token Tracking**:
```python
response = await provider.call_llm(prompt)
print(response.token_usage)  # {"used": 1000, "max": 4000}
```

### `patcher/` - Code Patching

**Purpose**: Parse and apply unified diffs.

**Key Classes**:
- `UnifiedDiffParser` - Parse diff format
- `PatchHunk` - Individual hunk data
- `CodePatcher` - Apply patches with rollback

**Main Methods**:
```python
# Parse diff
hunks = UnifiedDiffParser.parse(unified_diff_string)

# Create patcher
patcher = CodePatcher(repo_path)

# Apply patch
result = await patcher.apply_patch(diff_content, strategy="fuzzy")

# Rollback if needed
await patcher.rollback_patch(file_path, backup_path)

# Cleanup old backups
await patcher.cleanup_backups(keep_count=10)
```

**Features**:
- Auto-backup before applying
- Strict/fuzzy matching strategies
- Automatic rollback on failure
- Backup retention management
- Located in `~/.voria/backups/`

### `executor/` - Test Execution

**Purpose**: Detect and run test suites.

**Key Classes**:
- `TestExecutor` - Main coordinator
- `TestStatus` - Result enum
- `TestResult` - Individual test result
- `TestSuiteResult` - Full suite results
- Framework parsers:
  - `PytestParser` - Python pytest
  - `JestParser` - JavaScript Jest
  - (extensible for others)

**Main Methods**:
```python
# Create executor
executor = TestExecutor(repo_path)

# Detect framework
framework = await executor.detect_framework()  # "pytest"|"jest"|None

# Run tests
result = await executor.run_tests()

# Format results
output = executor.format_results(result)
```

**Results Structure**:
```python
TestSuiteResult(
    framework="pytest",
    total=25,
    passed=24,
    failed=1,
    skipped=0,
    duration=2.5,
    results=[
        TestResult(name="test_api", status=TestStatus.PASSED, duration=0.1),
        TestResult(name="test_db", status=TestStatus.FAILED, message="timeout")
    ]
)
```

### `agent/` - Orchestration

**Purpose**: Main agent loop for issue fixing.

**Key Classes**:
- `AgentLoop` - Core orchestrator
- `LoopState` - State tracking
- `LoopAction` - Action enum

**Main Methods**:
```python
# Create agent
loop = AgentLoop(
    provider_name="openai",
    api_key="sk-...",
    repo_path="/repo"
)

# Initialize (setup provider)
await loop.initialize("gpt-5.4")

# Run full loop
result = await loop.run(
    issue_id=42,
    issue_description="Fix bug in parser"
)
```

**Loop Stages**:
1. `_step_plan()` - Generate fix strategy
2. `_step_patch()` - Generate diff
3. `_step_apply()` - Apply changes
4. `_step_test()` - Run tests
5. `_analyze_failure()` - Analyze if failed
6. Loop back or succeed

**Result Structure**:
```python
{
    "status": "success"|"failure"|"timeout",
    "iterations": 3,
    "plan": "Generated plan...",
    "patch": "Generated diff...",
    "test_results": {...},
    "errors": []
}
```

### `github/` - GitHub Integration

**Purpose**: Fetch issues and create PRs.

**Key Classes**:
- `GitHubClient` - Main client
- GitHub operations:
  - `fetch_issue(id)` - Get issue details
  - `create_pr(head, base, title, body)` - Create PR
  - `add_comment(issue_id, text)` - Add issue comment
  - `list_issues()` - Get issues

**Usage**:
```python
github = GitHubClient(token="ghp_...")
issue = await github.fetch_issue(42)
pr = await github.create_pr(
    head="voria-fix-42",
    base="main",
    title="Fix issue #42",
    body="Automatic fix by voria"
)
```

### `token_manager/` - Cost Tracking

**Purpose**: Track LLM spending and enforce budgets.

**Key Classes**:
- `TokenManager` - Main tracker
- `TokenBudget` - Per-provider budgets

**Usage**:
```python
manager = TokenManager()

# Log usage
manager.log_usage(
    provider="openai",
    tokens_used=1000,
    cost=0.05
)

# Check budget
if not manager.within_budget("openai"):
    raise BudgetExceededError()

# Get stats
stats = manager.get_stats()  # Total cost today, etc.
```

**Budget Defaults**:
```
modal:   $0.00/hr (free until Apr 30)
openai:  $5.00/hr
gemini:  $1.00/hr
claude:  $3.00/hr
```

### `setup/` - Configuration

**Purpose**: Interactive provider setup.

**Key Classes**:
- `ProviderSetup` - Configuration manager

**Usage**:
```python
setup = ProviderSetup()

# Interactive flow
config = await setup.setup_provider()
# → Choose provider
# → Enter API key
# → Select model
# → Save to ~/.voria/providers.json

# Get saved config
cfg = setup.get_provider_config("openai")

# List configured providers
providers = setup.list_configured()
```

##  Rust Core Modules

### `main.rs` - Entry Point

**Responsibilities**:
- Parse CLI arguments
- Initialize logging
- Dispatch to subcommands
- Exit code handling

**Key Functions**:
```rust
async fn main() -> Result<()>
async fn handle_plan(issue_id: u32) -> Result<()>
async fn handle_issue(issue_id: u32) -> Result<()>
async fn handle_apply(plan_id: &str) -> Result<()>
```

### `cli/mod.rs` - Command Dispatch

**Responsibilities**:
- Parse subcommands (plan, issue, apply)
- Validate arguments
- Route to handlers

**Subcommands**:
- `plan <issue_id>` - Plan a fix
- `issue <issue_id>` - Full automation
- `apply <plan_id>` - Apply saved plan

### `ipc/mod.rs` - NDJSON Protocol

**Responsibilities**:
- Spawn Python subprocess
- Send NDJSON requests
- Receive NDJSON responses
- Timeout detection

**Key Structs**:
```rust
pub struct ProcessManager {
    child: Child,
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
}

impl ProcessManager {
    async fn send_request(&mut self, req: &Value) -> Result<()>
    async fn read_response(&mut self) -> Result<Value>
    async fn with_timeout(&mut self, req: &Value, secs: u64) -> Result<Value>
}
```

### `orchestrator/mod.rs` - Coordination

**Responsibilities**:
- Coordinate Rust-Python workflow
- Handle multi-step commands
- Error recovery

### `config/mod.rs` - Configuration

**Responsibilities**:
- Load config files
- Override with CLI flags
- Merge environment variables

### `ui/mod.rs` - Terminal UI

**Responsibilities**:
- Colored output (Blue/Green/Red)
- Progress display
- Error formatting

**Key Functions**:
```rust
fn print_info(msg: &str)     // Blue [i]
fn print_success(msg: &str)  // Green [✓]
fn print_error(msg: &str)    // Red [✗]
fn print_warning(msg: &str)  // Yellow [!]
```

##  Plugin Architecture

### Language Plugins

Location: `python/voria/plugins/`

**Plugin Structure**:
```python
class PythonPlugin:
    async def parse_code(self, source: str) -> AST
    async def run_tests(self, path: str) -> TestResult
    async def format_code(self, source: str) -> str
```

**Supported Languages**:
- Python (pytest)
- JavaScript/TypeScript (Jest)
- (Extensible)

##  Data Structures

### LLM Response

```python
class LLMResponse:
    content: str                    # Response text
    tokens_used: int                # Tokens consumed
    finish_reason: str              # "stop"|"length"|"error"
    metadata: Dict[str, Any]        # Provider-specific
```

### Patch Hunk

```python
@dataclass
class PatchHunk:
    old_file: str                   # File path
    new_file: str
    old_start: int                  # Starting line (1-indexed)
    old_count: int                  # Num lines before
    new_start: int                  # Starting line after
    new_count: int                  # Num lines after
    lines: List[str]                # Diff lines
```

### Test Result

```python
@dataclass
class TestResult:
    name: str                       # Test identifier
    status: TestStatus              # PASSED|FAILED|SKIPPED|ERROR
    duration: float                 # Seconds
    message: str                    # Fail message (if any)
    error_type: Optional[str]       # Exception type
    stacktrace: Optional[str]       # Full trace
```

##  Usage Patterns

### Using an LLM Provider

```python
# 1. Create provider
provider = LLMProviderFactory.create("openai", api_key, "gpt-5.4")

# 2. Call methods
plan = await provider.plan(issue_description)
patch = await provider.generate_patch(context, plan)

# 3. Check tokens
print(f"Used: {plan.tokens_used} tokens")
```

### Using the Agent Loop

```python
# 1. Create loop
loop = AgentLoop("openai", api_key, repo_path="/repo")

# 2. Initialize
await loop.initialize("gpt-5.4")

# 3. Run
result = await loop.run(issue_id=42, issue_description="...")

# 4. Check result
if result["status"] == "success":
    print("Issue fixed!")
else:
    print(f"Failed: {result['errors']}")
```

### Using Patching & Testing

```python
# 1. Create patcher
patcher = CodePatcher("/repo")

# 2. Apply patch
result = await patcher.apply_patch(diff_text)

# 3. Create executor
executor = TestExecutor("/repo")

# 4. Run tests
test_result = await executor.run_tests()

# 5. Check results
if test_result.passed == test_result.total:
    print("All tests pass!")
```

##  Dependencies

### Python
- httpx 0.24.0 - Async HTTP
- aiofiles 23.0 - Async file I/O
- pytest - Testing

### Rust
- tokio 1.51 - Async runtime
- serde_json - JSON
- colored - Terminal colors
- clap - CLI args

---

**See Also:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) - Why these choices
