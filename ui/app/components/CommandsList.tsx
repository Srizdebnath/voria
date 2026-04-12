interface Command {
  name: string;
  desc: string;
}

interface CommandsListProps {
  commands: Command[];
}

export function CommandsList({ commands }: CommandsListProps) {
  return (
    <ul className="command-list">
      {commands.map((cmd, index) => (
        <li key={index} className="command-item">
          <div className="command-name">
            <code style={{ background: '#0a0a0a', color: '#00ff88', padding: '0.25rem 0.5rem', marginRight: '0.5rem' }}>
              {cmd.name}
            </code>
          </div>
          <p className="command-desc">{cmd.desc}</p>
        </li>
      ))}
    </ul>
  );
}