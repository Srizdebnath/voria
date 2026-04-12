interface Command {
  cmd: string;
  desc: string;
}

interface TerminalCommandsProps {
  commands: Command[];
}

export function TerminalCommands({ commands }: TerminalCommandsProps) {
  return (
    <div className="terminal-window">
      <div className="terminal-header">
        <span className="terminal-dot" style={{ background: '#ff5f56' }}></span>
        <span className="terminal-dot" style={{ background: '#ffbd2e' }}></span>
        <span className="terminal-dot" style={{ background: '#27c93f' }}></span>
        <span className="terminal-title">voria — 80×24</span>
      </div>
      <div className="terminal-body">
        {commands.map((cmd, index) => (
          <div key={index} className="command-line">
            <span className="prompt">$</span>
            <span className="command">{cmd.cmd}</span>
            <span className="comment"># {cmd.desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}