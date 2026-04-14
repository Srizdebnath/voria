# Changelog

All notable changes to voria are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/v0.0.3/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.0.5] - April 14, 2026 ✅ TIER 1: SECURITY, STREAMING & RELIABILITY

### 🛡️ Pentesting CLI (Enhanced)
- **25+ Security Audits** running in parallel with `voria scan all`
- **SARIF Support:** Export results for GitHub Security tab integration (`voria ci`)
- **Security Diff:** Compare posture between git refs (`voria diff`)
- **Watch Mode:** Automatic re-testing on file changes (`voria watch`)

### ⚡ Performance & Reliability
- **HTTP Benchmarking:** Real-world load testing with latency distribution (`voria benchmark`)
- **Improved Stress Tests:** Real-time metrics for CPU, Memory, and Network tests
- **NVIDIA Integrated API Support:** Native support for MiniMax model v2.7

### 🤖 LLM & UX
- **Streaming Output:** Real-time token-by-token streaming for plan and fix commands
- **Auto-Fix:** AI-powered bug fixing with automatic patch application (`voria fix --auto`)
- **Premium Blue UI:** Completely revamped CLI aesthetic with professional formatting
- **Daemon-Ready IPC:** Infrastructure for persistent background engine acceleration

## [v0.0.3] - April 12, 2026 ✅ ADVANCED ANALYSIS & CHINESE MODELS

### 🔭 Advanced Code Analysis (New)
- **Hierarchical Dependency Graph** via `voria --graph`
- **Level-by-level visualization** (Root → Level 1 → Level 2)
- **Risk Integrity Scoring** based on coupling and complexity
- **Hot Spot Detection** for complex/unstable modules
- **Super-fast Rust implementation** for non-LLM static analysis
- **Progress interaction** with estimated time remaining
- **Automatic filtering** of generated/hidden directories (`.next`, `dist`, `build`)

### 🤖 Expanded Model Support
- Support for **Kimi**, **Minimax**, **DeepSeek**, and **SiliconFlow**
- **Detailed model selection** wizard in `voria --init`
- Unified model configuration across all providers

### 🔗 Support & Community
- **WhatsApp Support Group:** https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE?mode=gi_t
- **Documentation Overhaul:** Updated all docs to v0.0.3
- **Enhanced Contributor Setup:** Improved local development guides

## [v0.0.3] - April 12, 2026 ✅ PRODUCTION RELEASE

### 🎉 Major Release: Feature Complete

All planned features through Phase 8 are now complete and production-ready.

###  Phase 4: LLM Integration (COMPLETE)
- **Full CLI integration** with `voria plan` and `voria issue` commands
- **5 LLM providers** fully integrated:
  - OpenAI (GPT-5.4, GPT-5.4-mini)
  - Anthropic Claude (Claude 4.6 series)
  - Google Gemini (Gemini 3.x series)
  - Modal Z.ai (GLM-5.1-FP8)
  - Kimi (fallback support)
- **Dynamic model discovery** for all providers
- **Token tracking and budgeting** system
- **API key management** with secure storage
- **Model selection during setup** (`voria --init`)

###  Phase 5: GitHub Integration (COMPLETE)
- **Issue fetching** from GitHub API
- **PR auto-creation** with customizable titles
- **Commit management** with proper attribution
- **Branch handling** for feature branches
- **Status updates** to issues and PRs
- **Comment integration** for feedback and logs

###  Phase 6: Code Analysis & Patching (COMPLETE)
- **Multi-language code parsing** (Python, JS, Go, Java, Rust, Ruby, PHP, C++, C#)
- **LLM-powered code generation** with 5 providers
- **Unified diff format** support with full parsing
- **Safe patch application** with automatic rollback
- **Merge conflict detection** and resolution
- **Backup management** with cleanup policies

###  Phase 7: Testing & Validation (COMPLETE)
- **Multi-framework test execution:**
  - pytest (Python)
  - jest (JavaScript/TypeScript)
  - go test (Go)
  - junit (Java)
  - Custom framework detection
- **Failure analysis and logging**
- **Iterative refinement** (up to 5 iterations)
- **Framework auto-detection**
- **Test result integration** with agent loop

###  Phase 8: Agent Loop & Orchestration (COMPLETE)
- **Full workflow orchestration** (Plan → Patch → Apply → Test → Analyze → Iterate)
- **Intelligent iteration** with failure tracking
- **Error recovery** and graceful fallbacks
- **State tracking** for debugging
- **Progress visualization** in CLI

###  Bug Fixes
- Fixed RuntimeWarning in ModalProvider `__del__` method
- Proper async cleanup handling
- Event loop compatibility improvements

###  Documentation Updates
- **ROADMAP.md** - Updated with all completed phases
- **README.md** - Updated status and roadmap
- **INSTALL.md** - Simplified for npm installation
- **QUICKSTART.md** - Updated for npm-based setup
- **MODULES.md** - Current API documentation
- **New CHANGELOG.md** - This file

###  Distribution
- **Published to npm** as `@voria/cli@0.0.3`
- **Global CLI tool** - Install with `npm install -g @voria/cli`
- **Pre-built binaries** - No build required for end users

###  Testing
- **Test Coverage:** 100% pass rate
- **CLI tests:** ✅ All passed
- **Integration tests:** ✅ All passed
- **Phase 2 integration:** ✅ Complete
- **No critical bugs** identified

###  Quality Metrics
- ✅ All 8 planned phases complete
- ✅ 5 LLM providers integrated
- ✅ Multi-framework test support
- ✅ GitHub API integration
- ✅ Safe, reversible patch application
- ✅ Cost tracking and budgeting
- ✅ Production-ready code

---

## [v0.0.3] - April 2026

###  Phase 3: Configuration & Setup
- Interactive setup wizard (`voria --init`)
- LLM provider selection
- API key management
- Budget configuration
- Test framework detection
- Configuration persistence
- Per-project settings (`.voria.json`)
- Global settings (`~/.voria/config.json`)

###  Phase 2: Automation Foundation
- Multi-iteration refinement (up to 5 iterations)
- Automatic test execution
- Token budget management
- Basic LLM integration
- Plugin architecture

---

## [v0.0.3] - April 2026

###  Phase 1: Core Foundation
- Rust CLI base structure
- Python engine with NDJSON IPC
- Process management
- Basic command parsing
- Configuration file handling

---

##  Roadmap: Upcoming Releases

### v0.1.0 (Q2 2026) - Advanced Analysis
- Dependency graph analysis
- File relationship mapping
- Risk scoring system
- Context-aware code selection
- Performance optimizations

### v0.2.0 (Q3 2026) - Enterprise
- Team management
- Role-based access control
- Audit logging
- Cost allocation
- Team collaboration features

### vv0.0.3 (Q4 2026) - Stable API
- Stable API guarantees
- VS Code extension
- GitHub Actions integration
- Self-hosted deployment
- IDE integrations (JetBrains, IntelliJ)

---

##  Completion Status

| Phase | Name | Status | Version |
|-------|------|--------|---------|
| 1 | Foundation | ✅ Complete | v0.0.3 |
| 2 | Automation | ✅ Complete | v0.0.3 |
| 3 | Setup & Config | ✅ Complete | v0.0.3 |
| 4 | LLM Integration | ✅ Complete | v0.0.3 |
| 5 | GitHub Integration | ✅ Complete | v0.0.3 |
| 6 | Code Analysis | ✅ Complete | v0.0.3 |
| 7 | Testing & Validation | ✅ Complete | v0.0.3 |
| 8 | Agent Loop | ✅ Complete | v0.0.3 |
| 9 | Advanced Analysis | 📋 Planned | v0.1.0 |
| 10 | Enterprise | 📋 Planned | v0.2.0 |

---

##  Contributors

- Srizdebnath - Creator and Lead Developer

---



---

##  Links

- **GitHub:** https://github.com/Srizdebnath/voria
- **npm:** https://www.npmjs.com/package/@voria/cli
- **Issues:** https://github.com/Srizdebnath/voria/issues
- **Discussions:** https://github.com/Srizdebnath/voria/discussions
- **WhatsApp Support:** https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE?mode=gi_t

---

**Join our WhatsApp Support Group:** [Click Here](https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE?mode=gi_t)
