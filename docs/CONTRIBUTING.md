# Contributing to voria

Guidelines for contributing to the voria project.

##  Welcome Contributors!

voria is a community project. We welcome contributions from people of all experience levels—from fixing documentation to implementing complex features.

**Not sure where to start?** Check [#good-first-issue](https://github.com/Srizdebnath/voria/labels/good-first-issue) on GitHub.

---

##  Getting Started

### 1. Fork & Clone
```bash
# Fork on GitHub, then:
git clone https://github.com/Srizdebnath/voria.git
cd voria
```

### 2. Set Up Development Environment
```bash
# See DEVELOPMENT.md for full setup
# Quick version:
cd rust && cargo build
cd ../python && pip install -e .
```

### 3. Create a Branch
```bash
# Follow conventional naming
git checkout -b feature/my-feature
git checkout -b fix/issue-123
git checkout -b docs/update-readme
```

### 4. Make Changes & Test
```bash
# Write code
# Run tests
cd rust && cargo test
cd ../python && pytest

# Check formatting
cargo fmt && cargo clippy
black . && mypy .
```

### 5. Commit with Conventional Commits
```bash
git commit -m "feat: add new LLM provider support"
git commit -m "fix: resolve issue #123"
git commit -m "docs: update installation guide"
git commit -m "test: add test for graph analyzer"
git commit -m "refactor: simplify token manager"
```

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Test coverage
- `refactor`: Code cleanup (no behavior change)
- `perf`: Performance improvement
- `ci`: CI/CD changes

### 6. Push & Create Pull Request
```bash
git push origin feature/my-feature
# Go to GitHub and create pull request
```

---

##  Project Structure

```
voria/
├── rust/                    # Rust CLI and orchestration
│   ├── src/
│   │   ├── main.rs         # Entry point
│   │   ├── cli.rs          # Command-line interface
│   │   ├── ipc.rs          # NDJSON IPC protocol
│   │   ├── orchestrator.rs # Main orchestration
│   │   ├── config.rs       # Configuration management
│   │   └── ui.rs           # Output formatting
│   ├── Cargo.toml
│   └── tests/              # Integration tests
│
├── python/                 # Python core logic
│   ├── voria/
│   │   ├── core/
│   │   │   ├── llm/        # LLM providers & discovery
│   │   │   ├── patcher/    # Code patching (diff apply)
│   │   │   ├── executor/   # Test execution
│   │   │   ├── agent/      # Main orchestration loop
│   │   │   └── github/     # GitHub integration
│   │   ├── plugins/        # Plugin system
│   │   ├── utils/          # Utilities
│   │   └── engine.py       # NDJSON protocol handler
│   ├── tests/              # Unit & integration tests
│   ├── setup.py
│   └── requirements.txt
│
├── docs/                   # Documentation (Markdown)
│   ├── README.md           # Start here
│   ├── QUICKSTART.md       # 5-minute setup
│   ├── USER_GUIDE.md       # How to use voria
│   ├── EXAMPLES.md         # Real-world examples
│   ├── ARCHITECTURE.md     # System design
│   ├── IPC_PROTOCOL.md     # NDJSON protocol spec
│   ├── DESIGN_DECISIONS.md # Why things are the way they are
│   ├── MODULES.md          # API reference
│   ├── DEVELOPMENT.md      # Development setup
│   ├── CONTRIBUTING.md     # This file
│   ├── PLUGINS.md          # Plugin development
│   ├── LLM_INTEGRATION.md  # Adding new LLM providers
│   ├── PERFORMANCE.md      # Optimization guide
│   ├── SECURITY.md         # Security practices
│   ├── TROUBLESHOOTING.md  # Common issues & solutions
│   └── ROADMAP.md          # Feature roadmap
│
├── README.md               # Project overview
├── Cargo.toml              # Rust workspace config
└── Cargo.lock
```

---

##  Testing

### Python Tests
```bash
cd python

# Run all tests
pytest

# Run specific test
pytest tests/test_patcher.py::test_apply_patch

# With coverage
pytest --cov=voria

# Verbose output
pytest -vv
```

### Rust Tests
```bash
cd rust

# Run all tests
cargo test

# Run specific test
cargo test test_command_parsing

# With output
cargo test -- --nocapture
```

### Integration Tests
```bash
# Full workflow test (all systems)
./script/test-integration.sh

# Specific integration test
cd tests && python3 test_end_to_end.py
```

### Manual Testing
```bash
# Test locally modified code
cd rust
cargo build

cd ../python
pip install -e .

# Run test command
./target/release/voria plan 123
```

---

##  Code Style

### Python
We use:
- **Black** for formatting
- **MyPy** for type checking
- **Pylint** for linting
- **Google-style docstrings**

```bash
cd python

# Format code
black .

# Type checking
mypy .

# Linting
pylint voria/

# Before commit, run all:
black . && mypy . && pylint voria/ && pytest
```

**Example Python style:**
```python
"""Module docstring describing the module."""

from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class CodePatcher:
    """Applies patches to source code files.
    
    Attributes:
        backup_dir: Directory for storing backups
        verify_checksum: Whether to verify checksums
    """
    
    def __init__(self, backup_dir: str, verify_checksum: bool = True):
        """Initialize the patcher.
        
        Args:
            backup_dir: Path to backup directory
            verify_checksum: Whether to verify file checksums
        """
        self.backup_dir = backup_dir
        self.verify_checksum = verify_checksum
    
    def apply_patch(self, filepath: str, patch: str) -> bool:
        """Apply a unified diff patch to a file.
        
        Args:
            filepath: Path to the file to patch
            patch: Unified diff format patch
            
        Returns:
            True if patch applied successfully, False otherwise
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If patch is invalid
        """
        # Implementation here
        pass
```

### Rust
We use:
- **rustfmt** for formatting
- **clippy** for linting

```bash
cd rust

# Format code
cargo fmt

# Linting
cargo clippy -- -D warnings

# Before commit:
cargo fmt && cargo clippy && cargo test
```

**Example Rust style:**
```rust
use std::path::PathBuf;

/// Applies patches to source code.
#[derive(Debug)]
pub struct CodePatcher {
    backup_dir: PathBuf,
    verify_checksum: bool,
}

impl CodePatcher {
    /// Creates a new code patcher.
    ///
    /// # Arguments
    ///
    /// * `backup_dir` - Directory for storing backups
    /// * `verify_checksum` - Whether to verify checksums
    pub fn new(backup_dir: PathBuf, verify_checksum: bool) -> Self {
        CodePatcher {
            backup_dir,
            verify_checksum,
        }
    }

    /// Applies a unified diff patch to a file.
    ///
    /// # Arguments
    ///
    /// * `filepath` - Path to the file to patch
    /// * `patch` - Unified diff format patch
    ///
    /// # Returns
    ///
    /// `Result<(), PatchError>` indicating success or failure
    pub fn apply_patch(&self, filepath: &str, patch: &str) -> Result<(), PatchError> {
        // Implementation here
        Ok(())
    }
}
```

---

##  Pull Request Process

### Before Submitting PR

- [ ] **Tests pass** - `cargo test` and `pytest` succeed
- [ ] **Code is formatted** - `cargo fmt`, `black .`
- [ ] **Linting passes** - `cargo clippy`, `mypy .`
- [ ] **Tests added** - New features have tests
- [ ] **Documentation updated** - Docs reflect changes
- [ ] **Changelog noted** - Add entry to version history (if applicable)

### PR Checklist

```markdown
## Description
Brief description of your changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added new test cases
- [ ] Tested manually with: [describe]

## Documentation
- [ ] Updated relevant .md files
- [ ] Added docstrings
- [ ] Updated examples

## Breaking Changes
- [ ] This is a breaking change
- [ ] If yes, describe migration path
```

### What to Expect

1. **Review** - A maintainer will review within 48 hours
2. **Feedback** - We might request changes
3. **Merge** - Once approved, your code goes in! 🎉

---

##  Types of Contributions

### Bug Reports 
Found a bug? Create an issue with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Rust version, Python version)
- Screenshots/logs if helpful

### Documentation 
Help is always welcome to:
- Fix typos
- Clarify instructions
- Add examples
- Improve organization
- Translate to other languages

### New Features 
Before starting a big feature:
1. **Check** open issues - might already be planned
2. **Discuss** on GitHub Discussions
3. **Implement** when approved
4. **Test** thoroughly
5. **Document** clearly

### Plugin Development 
Create plugins for:
- New languages ([PLUGINS.md](PLUGINS.md))
- New VCS systems (Git, Hg, Perforce)
- New CI/CD systems (Jenkins, GitLab CI)
- New LLM providers ([LLM_INTEGRATION.md](LLM_INTEGRATION.md))

---

##  Code of Conduct

### Be Respectful
- Welcome newcomers and help them get started
- Assume good intent
- Address problems directly and professionally

### Be Inclusive
- Use inclusive language
- Consider diverse perspectives
- Make space for different experience levels

### Be Collaborative
- Ask questions instead of making assumptions
- Explain your reasoning
- Help others succeed

---

##  Questions?

- **GitHub Issues** - For bugs and specific problems
- **GitHub Discussions** - For questions and ideas
- **Email** - support@voria.dev for serious concerns

---

##  Thank You!

Every contribution - big or small - helps make voria better. Thank you for being part of this project!

---

**Next Steps:**
- Read [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup
- Check out [good-first-issue](https://github.com/Srizdebnath/voria/labels/good-first-issue) on GitHub
- Join our [Discord community](https://discord.gg/voria)

---

**See Also:**
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup and workflow
- [ROADMAP.md](ROADMAP.md) - Where we're heading
- [PLUGINS.md](PLUGINS.md) - Plugin development guide
- [LLM_INTEGRATION.md](LLM_INTEGRATION.md) - Adding LLM providers
