# voria v0.0.5

**AI-Powered Security, Reliability & Bug-Fixing Engine**

voria is a next-generation CLI tool that combines advanced AI code analysis with automated security pentesting and production reliability audits. Whether you're fixing a logic bug, generating a pull request, or performing a full security audit, voria handles the heavy lifting with precision and speed.

---

## 🚀 Key Features in v0.0.5

- **⚡ Streaming Output** - Real-time LLM response streaming (token-by-token) for instant feedback.
- **🛡️ Full Security Scan (`voria scan`)** - Run 25+ security audits (SQLi, XSS, SSRF, etc.) in parallel.
- **👁️ Watch Mode (`voria watch`)** - Continuous codebase monitoring with automatic security re-validation.
- **🔥 Performance Benchmarking (`voria benchmark`)** - Real-world HTTP load testing with p95/p99 latency analysis.
- **🖇️ CI/CD Integration (`voria ci`)** - Export SARIF reports directly to GitHub Security dashboard.
- **🛠️ Auto-Fix (`voria fix --auto`)** - AI generation and automatic patch application in one command.
- **🔷 Premium Blue Theme** - Professional, high-contrast CLI interface with rich formatting.
- **🏗️ Hybrid Architecture** - Blazing fast Rust CLI paired with a flexible Python AI engine.

---

## 📦 Installation

```bash
npm install -g @voria/cli
```

### Initial Setup
```bash
voria --init
```
Follow the interactive wizard to configure your LLM provider (OpenAI, Claude, Gemini, Modal, DeepSeek, Kimi, MiniMax, or SiliconFlow), set your security budget, and select your test framework.

---

## 🛡️ Pentesting & Security

voria is now a first-class security tool. It analyzes your code and infrastructure to find and optionally fix vulnerabilities.

### Full Project Scan
```bash
voria scan all
```
Performs a deep audit of your entire project, reporting on SQL Injection, Cross-Site Scripting, Insecure Direct Object References, and more.

### Security Diff
Compare two branches or commits to ensure no new vulnerabilities were introduced.
```bash
voria diff main feature-br
```

### Watch Mode
Keep voria running while you code. It will detect file changes and instantly re-run relevant security checks.
```bash
voria watch sql_injection,xss
```

---

## ⚡ Reliability & Performance

Ensure your production code can handle the heat.

### HTTP Benchmarking
```bash
voria benchmark https://api.myapp.com --requests 1000 --concurrency 50
```
Generates professional reports with latency distribution (Min, Max, P50, P95, P99) and status code counts.

### Resilience Testing
```bash
voria test cpu_stress
voria test mem_stress
voria test network_latency
```

---

## 🤖 AI Bug Fixing

The core voria engine for automated issue resolution.

### Fix from GitHub Issue
```bash
voria fix 123 ansh/voria --auto
```
Fetches issue #123, analyzes the code, generates a patch, applies it, and verified the fix.

### Interactive Planning
```bash
voria plan "Implement JWT authentication in the auth module"
```

---

## 🛠️ Commands Reference

| Command | Action |
|---------|--------|
| `voria --init` | Interactive configuration wizard |
| `voria scan <cat>` | Run full security audit (e.g., `all`, `owasp`, `logic`) |
| `voria test <id>` | Run a specific test case (e.g., `sql_injection`, `deadlock`) |
| `voria fix <id>` | AI-power fix for a GitHub issue |
| `voria fix --auto` | Generate and apply fix immediately |
| `voria watch` | Monitor files and re-run tests on change |
| `voria benchmark` | High-performance HTTP load testing |
| `voria diff <a..b>` | Compare security posture between refs |
| `voria ci` | Generate SARIF report for CI pipelines |
| `voria --graph` | Visualize security health distribution |

---

## 📖 Documentation

- **[Installation Guide](docs/INSTALL.md)**
- **[Full Security Suite](docs/SECURITY_TESTS.md)**
- **[Architecture Deep-Dive](docs/ARCHITECTURE.md)**
- **[CI/CD Integration Guide](docs/CICD.md)**

---

## 🤝 Community & Support

- **[WhatsApp Support](https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE)**
- **[GitHub Discussions](https://github.com/Srizdebnath/voria/discussions)**
- **[Bug Reports](https://github.com/Srizdebnath/voria/issues)**

License: MIT | Version: 0.0.5

**Want to contribute?**
→ [Contributor Guide](docs/CONTRIBUTING.md)

**Curious how it works?**
→ [Architecture Guide](docs/ARCHITECTURE.md)
