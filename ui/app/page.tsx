import { GitStars } from './components/GitStars';
import { TerminalCommands } from './components/TerminalCommands';

export default function Home() {
  const commands = [
    { cmd: 'voria --init', desc: 'Initialize voria in your project' },
    { cmd: 'voria setup-modal [TOKEN]', desc: 'Setup Modal LLM (free tier)' },
    { cmd: 'voria setup-openai [TOKEN]', desc: 'Setup OpenAI GPT-4' },
    { cmd: 'voria setup-claude [TOKEN]', desc: 'Setup Anthropic Claude' },
    { cmd: 'voria setup-gemini [TOKEN]', desc: 'Setup Google Gemini' },
    { cmd: 'voria set-github-token', desc: 'Configure GitHub access token' },
    { cmd: 'voria list-issues [REPO]', desc: 'List all issues in a repository' },
    { cmd: 'voria fix <ISSUE> [REPO]', desc: 'Fix a GitHub issue automatically' },
    { cmd: 'voria plan <ISSUE>', desc: 'Plan how to fix an issue' },
    { cmd: 'voria apply <PLAN>', desc: 'Apply a previously generated patch' },
    { cmd: 'voria --config', desc: 'View/edit configuration' },
    { cmd: 'voria --version', desc: 'Check installed version' },
  ];

  const docs = [
    { name: 'README', path: '/docs/README.md' },
    { name: 'QUICKSTART', path: '/docs/QUICKSTART.md' },
    { name: 'INSTALL', path: '/docs/INSTALL.md' },
    { name: 'USER_GUIDE', path: '/docs/USER_GUIDE.md' },
    { name: 'EXAMPLES', path: '/docs/EXAMPLES.md' },
    { name: 'ARCHITECTURE', path: '/docs/ARCHITECTURE.md' },
    { name: 'DEVELOPMENT', path: '/docs/DEVELOPMENT.md' },
    { name: 'CONTRIBUTING', path: '/docs/CONTRIBUTING.md' },
    { name: 'MODULES', path: '/docs/MODULES.md' },
    { name: 'PLUGINS', path: '/docs/PLUGINS.md' },
    { name: 'LLM_INTEGRATION', path: '/docs/LLM_INTEGRATION.md' },
    { name: 'IPC_PROTOCOL', path: '/docs/IPC_PROTOCOL.md' },
    { name: 'CHANGELOG', path: '/docs/CHANGELOG.md' },
    { name: 'ROADMAP', path: '/docs/ROADMAP.md' },
    { name: 'SECURITY', path: '/docs/SECURITY.md' },
    { name: 'TROUBLESHOOTING', path: '/docs/TROUBLESHOOTING.md' },
  ];

  return (
    <div className="container">
      <section className="hero-section">
        <h1 className="logo">VORIA</h1>
        <p className="tagline">AI-Powered Bug Fixing Tool</p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="https://www.npmjs.com/package/@voria/cli" target="_blank" rel="noopener noreferrer" className="brutal-btn">
            npm →
          </a>
          <a href="https://github.com/Srizdebnath/voria" target="_blank" rel="noopener noreferrer" className="brutal-btn brutal-btn-secondary">
            github →
          </a>
        </div>
      </section>

      <GitStars />

      <section className="brutal-box">
        <h2 className="brutal-title">About</h2>
        <p>
          <strong>Voria</strong> is an AI-powered CLI tool that automatically fixes bugs and implements features in your codebase. 
          Describe an issue or provide a GitHub issue number, and Voria will generate a fix, test it, iterate on failures, 
          and create a pull request — all automatically.
        </p>
        <div className="terminal-window" style={{ marginTop: '1rem' }}>
          <div className="terminal-header">
            <span className="terminal-dot" style={{ background: '#ff5f56' }}></span>
            <span className="terminal-dot" style={{ background: '#ffbd2e' }}></span>
            <span className="terminal-dot" style={{ background: '#27c93f' }}></span>
            <span className="terminal-title">~</span>
          </div>
          <div className="terminal-body">
            <p style={{ margin: 0 }}><span className="prompt">$</span> voria fix 42 owner/repo</p>
            <p style={{ margin: 0, color: '#00ff88' }}>[✓] Analyzing issue...</p>
            <p style={{ margin: 0, color: '#00ff88' }}>[✓] Generating patch...</p>
            <p style={{ margin: 0, color: '#00ff88' }}>[✓] Running tests...</p>
            <p style={{ margin: 0, color: '#00ff88' }}>[✓] Creating PR...</p>
            <p style={{ margin: 0, color: '#00ff88' }}>✨ Done!</p>
          </div>
        </div>
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Commands</h2>
        <TerminalCommands commands={commands} />
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Visual Architecture</h2>
        <div className="code-block" style={{ whiteSpace: 'pre', fontSize: '0.75rem', lineHeight: '1.4' }}>
{`┌─────────────────────────────────────────────────────────────┐
│                      VORIA CLI                            │
│                  (Node.js - Entry Point)                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Command Dispatcher (--init, --config, fix, plan)      │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ UI Layer (Neo-brutalism Theme, ANSI styling)            │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ IPC Manager (Process orchestration, NDJSON)         │  │
│  └────────────────────────────────────────────────────────┘  │
│                      │                                       │
│                      │ NDJSON (stdin/stdout)               │
│                      ▼                                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Persistent Child Process
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VORIA ENGINE                            │
│                  (Python - AI Core)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Agent Loop (Plan → Patch → Apply → Test → Iterate)    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ LLM Adapters (Claude, OpenAI, Gemini, Modal, Kimi)    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ GitHub Client (Issues, PRs, Comments)                 │  │
│  ├────────────────────────────────────────────────────────┤  ��
│  │ Code Patcher & Test Executor                          │  │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ (Optional / Future)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VORIA HUB                              │
│                  (Rust - High Perf)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Fast FS Operations                                    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Parallel Computation                                │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘`}
        </div>
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Developer Docs</h2>
        <div className="docs-grid">
          {docs.map((doc, index) => (
            <a key={index} href={doc.path} className="doc-link">
              {doc.name}
            </a>
          ))}
        </div>
      </section>

      <footer className="footer">
        <p>
          <a href="https://www.npmjs.com/package/@voria/cli" target="_blank" rel="noopener noreferrer" className="brutal-link">
            npm install -g @voria/cli
          </a>
        </p>
        <p style={{ marginTop: '1rem' }}>
          Built by{' '}
          <a href="https://github.com/Srizdebnath" target="_blank" rel="noopener noreferrer" className="brutal-link">
            @Srizdebnath
          </a>
        </p>
      </footer>
    </div>
  );
}