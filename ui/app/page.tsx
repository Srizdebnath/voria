import { GitStars } from './components/GitStars';
import { CommandsList } from './components/CommandsList';

export default function Home() {
  const commands = [
    { name: 'voria --init', desc: 'Initialize voria in your project' },
    { name: 'voria setup-modal [TOKEN]', desc: 'Setup Modal LLM (free tier)' },
    { name: 'voria setup-openai [TOKEN]', desc: 'Setup OpenAI GPT-4' },
    { name: 'voria setup-claude [TOKEN]', desc: 'Setup Anthropic Claude' },
    { name: 'voria setup-gemini [TOKEN]', desc: 'Setup Google Gemini' },
    { name: 'voria set-github-token', desc: 'Configure GitHub access token' },
    { name: 'voria list-issues [REPO]', desc: 'List all issues in a repository' },
    { name: 'voria fix <ISSUE> [REPO]', desc: 'Fix a GitHub issue automatically' },
    { name: 'voria plan <ISSUE>', desc: 'Plan how to fix an issue' },
    { name: 'voria apply <PLAN>', desc: 'Apply a previously generated patch' },
    { name: 'voria --config', desc: 'View/edit configuration' },
    { name: 'voria --version', desc: 'Check installed version' },
  ];

  return (
    <div className="container">
      <section className="hero-section">
        <h1 className="logo">VORIA</h1>
        <p className="tagline">AI-Powered Bug Fixing Tool</p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="https://www.npmjs.com/package/@voria/cli" target="_blank" rel="noopener noreferrer" className="brutal-btn">
            NPM →
          </a>
          <a href="https://github.com/Srizdebnath/voria" target="_blank" rel="noopener noreferrer" className="brutal-btn brutal-btn-secondary">
            GitHub →
          </a>
          <a href="https://srizdebnath.gitbook.io/voria" target="_blank" rel="noopener noreferrer" className="brutal-btn">
            Docs →
          </a>
        </div>
      </section>

      <GitStars />

      <section className="brutal-box">
        <h2 className="brutal-title">About Voria</h2>
        <p>
          Voria is an AI-powered CLI tool that automatically fixes bugs and implements features in your codebase. 
          Describe an issue or provide a GitHub issue number, and Voria will generate a fix, test it, iterate on failures, 
          and create a pull request — all automatically.
        </p>
        <ul style={{ marginTop: '1rem', marginLeft: '1.5rem', listStyle: 'square' }}>
          <li>Global CLI Tool — Install once, use anywhere</li>
          <li>Automatic Code Analysis — Understands issues and code context</li>
          <li>AI-Powered Fixes — Uses Claude, GPT-4, Gemini, Modal, or other LLMs</li>
          <li>Validation & Testing — Runs your test suite to verify fixes</li>
          <li>Smart Iteration — Refines failed fixes up to 5 times</li>
          <li>GitHub Integration — Creates pull requests directly</li>
          <li>Cost Control — Set daily budgets, monitor token usage</li>
        </ul>
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Quick Start</h2>
        <div className="code-block">
          <code>{`# Install globally
npm install -g @voria/cli

# Initialize your project
voria --init

# Setup LLM provider
voria setup-modal YOUR_MODAL_TOKEN

# Setup GitHub token
voria set-github-token

# List issues
voria list-issues owner/repo

# Fix an issue
voria fix 42 owner/repo`}</code>
        </div>
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Commands</h2>
        <CommandsList commands={commands} />
      </section>

      <section className="brutal-box">
        <h2 className="brutal-title">Documentation</h2>
        <div className="nav-grid">
          <a href="https://srizdebnath.gitbook.io/voria" target="_blank" rel="noopener noreferrer" className="brutal-btn" style={{ textAlign: 'center' }}>
            📖 Full Docs
          </a>
          <a href="https://srizdebnath.gitbook.io/voria/quickstart" target="_blank" rel="noopener noreferrer" className="brutal-btn" style={{ textAlign: 'center' }}>
            🚀 Quick Start
          </a>
          <a href="https://srizdebnath.gitbook.io/voria/user-guide" target="_blank" rel="noopener noreferrer" className="brutal-btn" style={{ textAlign: 'center' }}>
            📖 User Guide
          </a>
          <a href="https://srizdebnath.gitbook.io/voria/architecture" target="_blank" rel="noopener noreferrer" className="brutal-btn" style={{ textAlign: 'center' }}>
            🏗 Architecture
          </a>
          <a href="https://srizdebnath.gitbook.io/voria/contributing" target="_blank" rel="noopener noreferrer" className="brutal-btn" style={{ textAlign: 'center' }}>
            🤝 Contributing
          </a>
          <a href="https://srizdebnath.gitbook.io/voria/troubleshooting" target="_blank" rel="noopener noreferrer" className="brutal-btn" style={{ textAlign: 'center' }}>
            🔧 Troubleshooting
          </a>
        </div>
      </section>

      <footer className="footer">
        <p>
          <a href="https://www.npmjs.com/package/@voria/cli" target="_blank" rel="noopener noreferrer" className="brutal-link">
            npm install -g @voria/cli
          </a>
        </p>
        <p style={{ marginTop: '1rem' }}>
          Built with ❤️ by{' '}
          <a href="https://github.com/Srizdebnath" target="_blank" rel="noopener noreferrer" className="brutal-link">
            @Srizdebnath
          </a>
        </p>
      </footer>
    </div>
  );
}