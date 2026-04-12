import fs from 'fs';
import path from 'path';
import { GitStars } from './components/GitStars';
import { TerminalCommands } from './components/TerminalCommands';

export default async function Home() {
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

  let docsFiles: string[] = [];
  try {
    const docsDir = path.join(process.cwd(), '../docs');
    if (fs.existsSync(docsDir)) {
      docsFiles = fs.readdirSync(docsDir).filter(f => f.endsWith('.md'));
    }
  } catch (error) {
    console.error("Error reading docs directory:", error);
  }

  const docs = docsFiles.map(file => ({
    name: file.replace('.md', ''),
    path: `/docs/${file.replace('.md', '')}`
  }));

  // Fallback if no docs are found
  if (docs.length === 0) {
    docs.push({ name: 'README', path: '/docs/README' });
  }

  return (
    <div className="container mx-auto px-4 max-w-5xl">
      <section className="hero-section text-center py-16">
        <h1 className="logo text-6xl md:text-8xl font-black mb-4 tracking-tighter">VORIA</h1>
        <p className="tagline text-xl md:text-2xl font-bold mb-8 text-gray-800">AI-Powered Bug Fixing Tool</p>
        <div className="flex gap-4 justify-center flex-wrap pt-4">
          <a href="https://www.npmjs.com/package/@voria/cli" target="_blank" rel="noopener noreferrer" className="brutal-btn flex items-center tracking-wide">
            NPM Package ↗
          </a>
          <a href="https://github.com/Srizdebnath/voria" target="_blank" rel="noopener noreferrer" className="brutal-btn brutal-btn-secondary flex items-center tracking-wide">
            GitHub Repo ↗
          </a>
        </div>
      </section>

      <GitStars />

      <section className="brutal-box">
        <h2 className="brutal-title">About</h2>
        <p>
          <strong>Voria</strong> is an AI-powered CLI tool that automatically fixes bugs and implements features in your codebase. 
          Describe an issue or provide a GitHub issue number, and Voria will generate a fix, test it, iterate on failures, 
          and create a pull request - all automatically.
        </p>
        <div className="terminal-window rounded-xl overflow-hidden mt-6 shadow-xl" style={{ background: '#1c1c1e', border: '1px solid #333' }}>
          <div className="terminal-header flex items-center px-4 py-3" style={{ background: '#2d2d30' }}>
            <div className="flex gap-2">
              <span className="w-3.5 h-3.5 rounded-full" style={{ background: '#ff5f56' }}></span>
              <span className="w-3.5 h-3.5 rounded-full" style={{ background: '#ffbd2e' }}></span>
              <span className="w-3.5 h-3.5 rounded-full" style={{ background: '#27c93f' }}></span>
            </div>
            <div className="flex-1 text-center text-xs font-semibold text-gray-400 font-sans tracking-wide">
              bash - 80×24
            </div>
          </div>
          <div className="terminal-body p-6 font-mono text-sm leading-relaxed" style={{ background: '#1c1c1e' }}>
            <div className="flex flex-wrap gap-2 mb-2">
              <span className="text-emerald-400 font-bold">$</span>
              <span className="text-cyan-300 font-medium">voria fix 42 owner/repo</span>
            </div>
            <p className="m-0 text-emerald-400 mb-1">[✓] Analyzing issue...</p>
            <p className="m-0 text-emerald-400 mb-1">[✓] Generating patch...</p>
            <p className="m-0 text-emerald-400 mb-1">[✓] Running tests...</p>
            <p className="m-0 text-emerald-400 mb-1">[✓] Creating PR...</p>
            <p className="m-0 text-emerald-400 mt-2">✨ Done!</p>
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
{`┌───────────────────────────────────────────────────────────────┐
│                      VORIA CLI                                │
│                  (Node.js - Entry Point)                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Command Dispatcher (--init, --config, fix, plan)       │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ UI Layer (Neo-brutalism Theme, ANSI styling)           │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ IPC Manager (Process orchestration, NDJSON)            │   |
│  └────────────────────────────────────────────────────────┘   │
│                      │                                        │
│                      │ NDJSON (stdin/stdout)                  │
│                      ▼                                        │
└───────────────────────────────────────────────────────────────┘
                         │
                         │ Persistent Child Process
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VORIA ENGINE                             │
│                  (Python - AI Core)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Agent Loop (Plan → Patch → Apply → Test → Iterate)    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ LLM Adapters (Claude, OpenAI, Gemini, Modal, Kimi)    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ GitHub Client (Issues, PRs, Comments)                 │  │
│  ├───────────────────────────────────────────────────────┤  |
│  │ Code Patcher & Test Executor                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ (Optional / Future)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VORIA HUB                                │
│                  (Rust - High Perf)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Fast FS Operations                                    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ Parallel Computation                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘`}
        </div>
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Developer Docs</h2>
        <div className="docs-grid mt-8">
          {docs.map((doc, index) => (
            <a 
              key={index} 
              href={doc.path} 
              className="doc-link flex items-center justify-center min-h-[60px] uppercase font-black tracking-tight"
            >
              {doc.name.replace(/_/g, ' ')}
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
            TEAM VORIA
          </a>
        </p>
      </footer>
    </div>
  );
}