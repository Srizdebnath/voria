# Contributing to Victory

Thank you for your interest in contributing to Victory! This document provides guidelines and workflows for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Contributing Workflow](#contributing-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Development Setup

### Prerequisites

- Rust 1.70+ (https://rustup.rs)
- Python 3.9+
- Git
- VS Code recommended (with Rust-analyzer extension)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Srizdebnath/victory.git
   cd victory
   ```

2. **Build Rust:**
   ```bash
   cd rust
   cargo build
   cargo test
   cd ..
   ```

3. **Setup Python:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   cd python
   pip install -e ".[dev]"
   cd ..
   ```

4. **Verify setup:**
   ```bash
   ./target/debug/victory --help
   ./target/debug/victory plan 1
   ```

## Contributing Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring

### 2. Make Changes

- Use this structure as a guide
- Write tests for new code
- Keep commits atomic
- Follow coding standards (see below)

### 3. Test Locally

```bash
# Rust
cd rust
cargo test
cargo clippy
cargo fmt
cd ..

# Python
cd python
black .
python -m pytest
cd ..

# End-to-end
./target/debug/victory -v plan 1
```

### 4. Commit with Clear Messages

```bash
git commit -m "fix(ipc): improve timeout handling

- Added exponential backoff for retries
- Better error messages for debugging
- Fixes #42"
```

### 5. Push and Open PR

```bash
git push origin feature/your-feature-name
```

Create a PR with:
- Clear title and description
- Reference to related issues
- Screenshots/logs if applicable

## Coding Standards

### Rust

**Style:**
- Run `cargo fmt` before committing
- Run `cargo clippy` and address warnings
- Document public APIs with doc comments

**Example:**
```rust
/// Spawns the Python engine subprocess
/// 
/// # Errors
/// Returns error if process spawn fails
pub async fn spawn_process(&self) -> Result<()> {
    // Implementation
}
```

**Testing:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parser_handles_empty_input() {
        assert_eq!(parse(""), None);
    }
}
```

### Python

**Style:**
- Run `black .` for formatting
- Use type hints: `def process(data: str) -> Dict[str, Any]:`
- Docstrings for all public functions

**Example:**
```python
def handle_plan_command(command: Dict[str, Any]) -> None:
    """Handle 'plan' command to analyze issue.
    
    Args:
        command: The NDJSON command dict
    """
    issue_id = command.get("issue_id")
    logger.debug(f"Processing plan for issue #{issue_id}")
```

**Testing:**
```python
def test_parse_json_request():
    """Test that JSON requests are parsed correctly."""
    request = json.loads('{"command":"plan","issue_id":1}')
    assert request["command"] == "plan"
    assert request["issue_id"] == 1
```

## Testing

### Run All Tests

```bash
# Rust
cd rust && cargo test && cd ..

# Python
cd python && python -m pytest && cd ..
```

### Write Tests

**Rust:**
- Tests go in the same file in a `tests` module
- Use descriptive function names: `test_spawn_on_invalid_python_fails()`

**Python:**
- Tests go in `tests/` directory
- Use pytest conventions
- Name files `test_*.py`

### Test Coverage

Aim for >80% coverage on:
- IPC protocol handling
- CLI argument parsing
- Process management

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `perf:` Performance improvement
- `test:` Test additions
- `chore:` Build, deps, etc.

**Scopes (Rust):**
- `cli` - CLI subcommands
- `ipc` - NDJSON communication
- `process` - Process management
- `config` - Configuration

**Scopes (Python):**
- `engine` - Main engine loop
- `llm` - LLM integrations
- `agent` - Agent loop
- `protocol` - NDJSON protocol

**Examples:**
```
fix(ipc): handle null bytes in JSON responses
feat(llm): add Gemini provider support
docs(architecture): clarify process lifecycle
```

## Pull Requests

### PR Requirements

1. **Clear title and description**
2. **Linked issues** (fixes #123)
3. **Tests included** for new code
4. **No failing CI/CD**
5. **Code review approval**

### PR Description Template

```markdown
## Description
Brief summary of changes.

## Motivation
Why is this change needed?

## Changes
- Specific change 1
- Specific change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commits are atomic and clear
- [ ] No breaking changes (or noted)
```

### Review Process

1. Automated checks run
2. At least one maintainer reviews
3. Feedback addressed
4. Approved and merged

## Key Areas for Contribution

### High Priority

- **LLM Integration** (`python/victory/core/llm/`)
  - Add provider support
  - Token management
  - Error handling

- **GitHub Integration** (`python/victory/core/github/`)
  - Issue fetching
  - PR management
  - Status updates

- **Agent Loop** (`python/victory/core/agent/`)
  - Planning logic
  - Iteration management
  - Success criteria

### Medium Priority

- Code parsing/analysis plugins
- Performance optimizations
- Better error messages
- Documentation improvements

### Good First Issues

- Add tests for existing code
- Improve error messages
- Add code comments
- Documentation updates

## Resources

- [Architecture Guide](../docs/ARCHITECTURE.md)
- [IPC Protocol](../docs/IPC_PROTOCOL.md)
- [Quick Start](../docs/QUICKSTART.md)
- Rust Book: https://doc.rust-lang.org/book/
- Python Docs: https://docs.python.org/3/

## Questions?

- Check existing issues/discussions
- Ask in issues or PRs
- Start a discussion

---

Thank you for contributing to Victory! 🚀
