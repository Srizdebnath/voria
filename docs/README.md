# voria Documentation

Welcome to voria's comprehensive documentation. This folder contains everything you need to understand, use, and contribute to voria.

##  Documentation Map

### Getting Started (Start Here!)
- **[INSTALL.md](INSTALL.md)** - Installation and setup instructions
- **[QUICKSTART.md](QUICKSTART.md)** - Get voria running in 5 minutes
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete usage guide and commands
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world usage examples

### Understanding voria
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and component overview
- **[IPC_PROTOCOL.md](IPC_PROTOCOL.md)** - NDJSON protocol specification
- **[DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)** - Why we made certain choices
- **[MODULES.md](MODULES.md)** - Detailed module documentation

### Development & Extension
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development environment setup
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributor guidelines
- **[PLUGINS.md](PLUGINS.md)** - Writing custom plugins
- **[LLM_INTEGRATION.md](LLM_INTEGRATION.md)** - Adding new LLM providers

### Operations & Reference
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance tuning and optimization
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[ROADMAP.md](ROADMAP.md)** - Feature roadmap and future plans

##  Quick Navigation

**I want to...**
- Get started → [QUICKSTART.md](QUICKSTART.md)
- Learn to use voria → [USER_GUIDE.md](USER_GUIDE.md)
- See examples → [EXAMPLES.md](EXAMPLES.md)
- Understand how it works → [ARCHITECTURE.md](ARCHITECTURE.md)
- Contribute code → [CONTRIBUTING.md](CONTRIBUTING.md)
- Set up development → [DEVELOPMENT.md](DEVELOPMENT.md)
- Write a plugin → [PLUGINS.md](PLUGINS.md)
- Add an LLM provider → [LLM_INTEGRATION.md](LLM_INTEGRATION.md)
- Fix a problem → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Optimize performance → [PERFORMANCE.md](PERFORMANCE.md)
- Check security → [SECURITY.md](SECURITY.md)

##  Reading Order

**For Users:**
1. [QUICKSTART.md](QUICKSTART.md)
2. [USER_GUIDE.md](USER_GUIDE.md)
3. [EXAMPLES.md](EXAMPLES.md)
4. [ARCHITECTURE.md](ARCHITECTURE.md) (optional, for understanding)

**For Developers:**
1. [DEVELOPMENT.md](DEVELOPMENT.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [IPC_PROTOCOL.md](IPC_PROTOCOL.md)
4. [MODULES.md](MODULES.md)
5. [CONTRIBUTING.md](CONTRIBUTING.md)

**For Contributors:**
1. [CONTRIBUTING.md](CONTRIBUTING.md)
2. [DEVELOPMENT.md](DEVELOPMENT.md)
3. [MODULES.md](MODULES.md)
4. Specific module docs (e.g., [PLUGINS.md](PLUGINS.md), [LLM_INTEGRATION.md](LLM_INTEGRATION.md))

##  voria Overview

voria is an AI-powered CLI tool that helps open source contributors fix issues automatically:

```bash
# Run one command
voria issue 42

# voria will:
# 1. Fetch issue from GitHub
# 2. Analyze the codebase
# 3. Plan a fix (using AI)
# 4. Generate code patches
# 5. Apply and test changes
# 6. Create a pull request
```

##  Architecture at a Glance

```
User Interface (Rust CLI)
    ↓
NDJSON Protocol (stdin/stdout)
    ↓
Python Engine (LLM + GitHub + Testing)
    ↓
LLM Providers (OpenAI, Gemini, Claude, Modal)
```

##  What's Included

- **Rust CLI** - High-performance command-line interface
- **Python Engine** - AI intelligence and orchestration
- **NDJSON Protocol** - Cross-platform IPC
- **LLM Support** - 4 AI providers (OpenAI, Gemini, Claude, Modal)
- **GitHub Integration** - Issue and PR automation
- **Test Orchestration** - Automatic testing and validation

##  Key Features

-  AI-powered issue analysis
-  Automatic code patch generation
-  Integrated test execution
-  Iterative refinement (up to 5 itrations)
-  Multi-provider LLM support
-  Automatic backup and rollback
-  Token usage tracking
-  Production-ready error handling

##  External Resources

- [GitHub Repository](https://github.com/Srizdebnath/voria)
- [Main README](../README.md)
- [Issue Tracker](https://github.com/Srizdebnath/voria/issues)
- [Discussions](https://github.com/Srizdebnath/voria/discussions)

##  Questions?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Read [EXAMPLES.md](EXAMPLES.md) for usage patterns
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution process
- Open an issue on GitHub

---

**Last Updated:** April 10, 2026
**Documentation Version:** 2.0
