import fs from 'fs';
import path from 'path';
import { GitStars } from './components/GitStars';
import { TerminalCommands } from './components/TerminalCommands';

export default async function Home() {
  const commands = [
    { cmd: 'voria --init', desc: 'Initialize project & choose LLM provider' },
    { cmd: 'voria scan', desc: 'Full security audit (XSS, SQLi, secrets)' },
    { cmd: 'voria benchmark <url>', desc: 'HTTP benchmarking (p95/p99 analysis)' },
    { cmd: 'voria watch', desc: 'Monitor files & re-run tests on change' },
    { cmd: 'voria fix <id> --auto', desc: 'Auto-apply fix and verify with tests' },
    { cmd: 'voria ci', desc: 'CI/CD scan — outputs SARIF for GitHub' },
    { cmd: 'voria --graph', desc: 'Visualize codebase dependency graph' },
    { cmd: 'voria status', desc: 'Show current project security health' },
    { cmd: 'voria --config', desc: 'Configure LLM providers and settings' },
    { cmd: 'voria --version', desc: 'Check installed version (v0.0.5)' },
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
          <strong>Voria</strong> is an AI-powered autonomous engine for codebase security, reliability, and bug-fixing. 
          It performs deep security audits (`voria scan`), high-performance benchmarking, and fully automated issue resolution 
          by generating patches, running tests, and managing PRs—powered by advanced LLMs like Claude 3.5, GPT-4o, and DeepSeek.
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
        <h2 className="brutal-title">Security & Reliability Suite</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="p-4 border-2 border-black bg-emerald-100 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="font-black text-lg mb-2">🔒 SECURITY</h3>
            <p className="text-xs font-bold leading-tight">SQLi, XSS, CSRF, JWT, SSRF, Hardcoded Secrets, XXE, and more.</p>
            <div className="mt-4 text-[10px] font-black uppercase tracking-tighter">24 SCANS AVAILABLE</div>
          </div>
          <div className="p-4 border-2 border-black bg-blue-100 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="font-black text-lg mb-2">🏭 RELIABILITY</h3>
            <p className="text-xs font-bold leading-tight">Deadlocks, Race Conditions, Memory Leaks, Connection Exhaustion.</p>
            <div className="mt-4 text-[10px] font-black uppercase tracking-tighter">10 SCANS AVAILABLE</div>
          </div>
          <div className="p-4 border-2 border-black bg-purple-100 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="font-black text-lg mb-2">⚡ PERFORMANCE</h3>
            <p className="text-xs font-bold leading-tight">P99 Latency, Concurrency, Throughput, Cold Starts, DB Indexing.</p>
            <div className="mt-4 text-[10px] font-black uppercase tracking-tighter">11 SCANS AVAILABLE</div>
          </div>
          <div className="p-4 border-2 border-black bg-yellow-100 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="font-black text-lg mb-2">💎 QUALITY</h3>
            <p className="text-xs font-bold leading-tight">License Compliance, Coverage Gaps, Complexity Drift, Linting.</p>
            <div className="mt-4 text-[10px] font-black uppercase tracking-tighter">7 SCANS AVAILABLE</div>
          </div>
        </div>
        <p className="mt-8 text-sm font-bold text-center italic">
          Run <code className="bg-gray-200 px-1">voria scan --category all</code> to execute the full 52-test audit.
        </p>
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Commands</h2>
        <TerminalCommands commands={commands} />
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Visual Architecture</h2>
        <div className="code-block" style={{ whiteSpace: 'pre', fontSize: '0.75rem', lineHeight: '1.4' }}>
{`┌─────────────────────────────────────────────────────────────────┐
│                      VORIA CLI (Rust)                           │
│                  (Performance Orchestrator)                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Commands (scan, fix, benchmark, watch, ci, --graph)     │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ High-Speed FS Operations & Parallel Execution           │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ IPC Manager (Process orchestration via NDJSON)          │    |
│  └─────────────────────────────────────────────────────────┘    │
│                      │                                          │
│                      │ NDJSON (stdin/stdout)                    │
│                      ▼                                          │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ Persistent Engine Hook
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VORIA ENGINE (Python)                    │
│                  (Autonomous AI Logic)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Agent Loop (Plan → Patch → Apply → Test → Iterate)    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ 🛡️ Security Audit Engine (SQli, XSS, Logic Scans)     │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ ⚡ Performance Probes & Benchmarking Logic             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ 🤖 Multi-LLM Adapters (Claude, OpenAI, Gemini, etc.)  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
`}
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