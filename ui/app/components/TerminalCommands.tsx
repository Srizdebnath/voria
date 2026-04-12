"use client";

import React from "react";

interface Command {
  cmd: string;
  desc: string;
}

interface TerminalCommandsProps {
  commands: Command[];
}

export function TerminalCommands({ commands }: TerminalCommandsProps) {
  return (
    <div className="terminal-window rounded-xl overflow-hidden" style={{ background: '#1c1c1e', border: '1px solid #333', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
      <div className="terminal-header flex items-center px-4 py-3" style={{ background: '#2d2d30' }}>
        <div className="flex gap-2">
          <span className="w-3.5 h-3.5 rounded-full" style={{ background: '#ff5f56' }}></span>
          <span className="w-3.5 h-3.5 rounded-full" style={{ background: '#ffbd2e' }}></span>
          <span className="w-3.5 h-3.5 rounded-full" style={{ background: '#27c93f' }}></span>
        </div>
        <div className="flex-1 text-center text-xs font-semibold text-gray-400 font-sans tracking-wide">
          voria - bash - 80×24
        </div>
      </div>
      <div className="terminal-body p-6 font-mono text-sm leading-relaxed" style={{ color: '#f3f3f3', background: '#1c1c1e' }}>
        {commands.map((cmd, index) => (
          <div key={index} className="flex items-center justify-between mb-3 gap-4 group">
            <div className="flex-1 min-w-0">
              <span className="text-emerald-400 font-bold">$ </span>
              <span className="text-cyan-300 font-medium">{cmd.cmd}</span>
              <span className="text-gray-500 italic ml-4 opacity-60"># {cmd.desc}</span>
            </div>
            <button 
              onClick={() => {
                navigator.clipboard.writeText(cmd.cmd);
              }}
              className="text-gray-500 hover:text-emerald-400 transition-colors p-1"
              title="Copy to clipboard"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}