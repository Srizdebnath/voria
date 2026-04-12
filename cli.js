#!/usr/bin/env node

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Get the voria binary path
const platform = os.platform();
const binaryName = platform === 'win32' ? 'voria.exe' : 'voria';
const binaryPath = path.join(__dirname, 'target', 'release', binaryName);

// Check if binary exists
if (!fs.existsSync(binaryPath)) {
  console.error('❌ voria binary not found. Please rebuild the package.');
  console.error(`Expected at: ${binaryPath}`);
  console.error('\nTry running: npm rebuild @voria/cli');
  process.exit(1);
}

// Make binary executable on Unix systems
if (platform !== 'win32') {
  fs.chmodSync(binaryPath, '0755');
}

// Pass all arguments to the binary
const args = process.argv.slice(2);
const child = spawn(binaryPath, args, {
  stdio: 'inherit'
});

// Forward exit code
child.on('exit', (code) => {
  process.exit(code || 0);
});

// Handle errors
child.on('error', (err) => {
  console.error('❌ Error running voria:', err.message);
  process.exit(1);
});
