# Troubleshooting Guide

Solutions to common Victory issues.

##  Installation Issues

### "cargo not found"

**Error:**
```
command not found: cargo
```

**Solution:**
```bash
# Install Rust
curl --proto '=https' --tlsvv0.0.1 -sSf https://sh.rustup.rs | sh

# Add to PATH
source $HOME/.cargo/env

# Verify
cargo --version
```

### "Python command not found"

**Error:**
```
python3: command not found
```

**Solution:**
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3

# Verify
python3 --version  # Should be 3.9+
```

### "Build fails: can't find Tokio"

**Error:**
```
error[E0432]: unresolved import `tokio`
```

**Solution:**
```bash
cd rust
cargo clean
cargo build
```

### "Python import error"

**Error:**
```
ModuleNotFoundError: No module named 'victory'
```

**Solution:**
```bash
cd python
pip install -e .

# Verify
python3 -c "import victory; print('OK')"
```

##  Runtime Issues

### "Command hangs or takes forever"

**Symptoms:**
- Command doesn't respond
- Cursor stuck

**Solutions:**

1. **Check if Python process is stuck:**
   ```bash
   # In another terminal
   ps aux | grep python
   
   # Kill the stuck process
   pkill -f victory.engine
   ```

2. **Increase timeout:**
   ```bash
   VICTORY_TIMEOUT=3600 ./target/release/victory plan 1
   ```

3. **Use different LLM** (might be down):
   ```bash
   ./target/release/victory plan 1 --llm gemini
   ```

4. **Check network:**
   ```bash
   # Can you access the LLM API?
   curl -I https://api.openai.com/
   ```

### "API Key not working"

**Error:**
```
Authentication failed
Unauthorized: Invalid API key
```

**Solutions:**

1. **Ensure key is set:**
   ```bash
   echo $OPENAI_API_KEY  # Should not be empty
   ```

2. **Check key is correct:**
   ```bash
   # Visit provider console to verify
   # https://platform.openai.com/logout (wait, this logs out)
   # https://platform.openai.com/account/api-keys
   ```

3. **Reconfigure:**
   ```bash
   python3 -m victory.core.setup
   # Choose provider → Enter key again → Select model
   ```

4. **Test key directly:**
   ```python
   import httpx
   import asyncio
   
   async def test():
       client = httpx.AsyncClient()
       resp = await client.post(
           "https://api.openai.com/v1/models",
           headers={"Authorization": f"Bearer {KEY}"}
       )
       print(resp.status_code)
   asyncio.run(test())
   ```

### "Patch apply fails"

**Error:**
```
Failed to apply patch: hunk FAILED
```

**Solutions:**

1. **Check patch is valid:**
   ```bash
   # Look at generated patchfile
   victory issue 42 --dry-run --verbose
   ```

2. **Try fuzzy matching:**
   ```bash
   victory issue 42 --patch-strategy fuzzy
   ```

3. **Rollback and retry:**
   ```bash
   # Recovery from auto-backup
   cp ~/.victory/backups/file_* restored_file
   ```

### "Tests fail after patch"

**Error:**
```
❌ Test suite failed
Tests: 24 passed, 1 failed
```

**Solutions:**

1. **Review generated code:**
   ```bash
   # View the patch that was applied
   git diff HEAD
   ```

2. **Increase iterations** (let Victory refine):
   ```bash
   victory issue 42 --max-iterations 5
   ```

3. **Use different LLM** (better quality):
   ```bash
   victory issue 42 --llm claude
   ```

4. **Check test output:**
   ```bash
   # Detailed test failure info
   pytest -vv  # Run locally
   ```

##  Cost & Token Issues

### "Token budget exceeded"

**Error:**
```
BudgetExceededError: Daily budget of $5.00 exceeded
```

**Solutions:**

1. **Check spending:**
   ```bash
   victory token info
   ```

2. **Increase budget:**
   ```bash
   python3 -m victory.core.setup  # Reconfigure
   ```

3. **Use cheaper LLM:**
   ```bash
   victory issue 42 --llm gemini  # Cheaper than OpenAI
   ```

4. **Skip iterations** (don't refine):
   ```bash
   victory issue 42 --max-iterations 1
   ```

### "High token usage"

**Symptom:**
- Tokens used much higher than expected

**Solutions:**

1. **Reduce context:**
   ```bash
   victory issue 42 --max-files 10 --exclude "tests/"
   ```

2. **Shorter prompts:**
   - Customize prompts in `~/.victory/prompts/`
   - Remove unnecessary instructions

3. **Use faster model:**
   ```bash
   victory issue 42 --model gpt-4-mini
   ```

##  Network Issues

### "Connection timeout"

**Error:**
```
Connection timeout: Unable to reach api.openai.com
```

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping google.com
   ```

2. **Check DNS:**
   ```bash
   nslookup api.openai.com
   ```

3. **Add network retry:**
   ```python
   # In settings
   victory_retry_count=3
   victory_retry_delay=2
   ```

4. **Use VPN** (if behind corporate proxy):
   ```bash
   # Configure system proxy
   export HTTP_PROXY="http://proxy:8080"
   export HTTPS_PROXY="https://proxy:8443"
   ```

### "TLS certificate error"

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions (Development only):**

```bash
# Disable cert verification (unsafe!)
export INSECURE_SKIP_VERIFY=true
victory plan 1

# Better: Update CA certificates
# macOS
/usr/local/opt/openssl/bin/c_rehash

# Linux
sudo update-ca-certificates
```

##  Protocol Issues

### "NDJSON protocol error"

**Error:**
```
JSON parsing error: extra data
PyErr_SetString: Protocol error
```

**Solutions:**

1. **Clear cache:**
   ```bash
   rm -rf ~/.victory/
   ```

2. **Reinstall Python:**
   ```bash
   cd python
   pip uninstall victory
   pip install -e .
   ```

3. **Check for corruption:**
   ```bash
   # Test protocol manually
   echo '{"command":"plan","issue_id":1}' | python3 -m victory.engine | head -1
   ```

### "Process communication broken"

**Symptoms:**
- Python subprocess crashes
- No response from engine

**Solutions:**

1. **Kill stray processes:**
   ```bash
   pkill -f victory.engine
   ```

2. **Check stderr for errors:**
   ```bash
   victory -v plan 1 2>&1 | tail -20
   ```

3. **Test Python directly:**
   ```bash
   python3 -m victory.engine  # See if it starts
   ```

##  Test Execution Issues

### "Framework not detected"

**Error:**
```
Could not detect test framework
```

**Solutions:**

1. **Specify manually:**
   ```bash
   victory issue 42 --test-cmd "pytest -v tests/"
   ```

2. **Check framework installed:**
   ```bash
   pytest --version
   # or
   npm test -- --version
   ```

3. **Verify test directory exists:**
   ```bash
   ls tests/
   ls test/
   # (check for capital T)
   ```

### "Tests timeout"

**Error:**
```
Test execution timeout: Exceeded 300s
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   victory issue 42 --test-timeout 600
   ```

2. **Run tests individually:**
   ```bash
   # Identify slow test
   pytest --durations=10  # Show 10 slowest
   ```

3. **Skip slow tests:**
   ```bash
   victory issue 42 --test-cmd "pytest -v -m 'not slow'"
   ```

##  Permission Issues

### "Permission denied"

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/repo/file.py'
```

**Solutions:**

```bash
# Check permissions
ls -la /repo/file.py

# Fix permissions
chmod 644 /repo/file.py
chmod 755 /repo/

# Or run with adequate permissions
sudo victory issue 42  # ⚠️ Use cautiously
```

### "Cannot write to backup directory"

**Error:**
```
PermissionError: ~/.victory/backups
```

**Solutions:**

```bash
# Create backup directory
mkdir -p ~/.victory/backups

# Fix permissions
chmod 700 ~/.victory/

# Verify
ls -ld ~/.victory/
```

##  Output Issues

### "Garbled output / strange characters"

**Symptoms:**
- Unicode characters not displaying
- Colored output broken

**Solutions:**

```bash
# Force UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Disable colors (if terminal doesn't support)
victory --no-color plan 1

# Verify terminal encoding
locale
```

### "No output at all"

**Symptoms:**
- Command runs but shows nothing

**Solutions:**

1. **Use verbose flag:**
   ```bash
   victory -v plan 1
   ```

2. **Check if running:**
   ```bash
   # In another terminal
   watch -n 1 'ps aux | grep victory'
   ```

3. **Check logs:**
   ```bash
   tail -f ~/.victory/victory.log
   ```

##  Getting Help

### Collect Debug Information

```bash
# Generate debug bundle
mkdir victory-debug
cd victory-debug

# Collect versions
echo "Rust:" && rustc --version && cargo --version
echo "Python:" && python3 --version
echo "Victory:" && ./target/release/victory --version

# Test setup
./target/release/victory --help > cli_help.txt
python3 -m victory.engine < /dev/null 2> engine.log

# System info
uname -a > system.txt
env | grep VICTORY > victory_env.txt

# Create bundle
tar czf victory-debug.tar.gz *.txt *.log

# Upload to issue
```

### Report an Issue

1. **Search existing issues** (might be solved)
2. **Create new issue** with:
   - Error message (full text)
   - Commands you ran
   - Expected behavior
   - Actual behavior
   - Debug bundle (if complex)
3. **Check** [GitHub Issues](https://github.com/Srizdebnath/Victory/issues)

### Ask for Help

- [GitHub Discussions](https://github.com/Srizdebnath/Victory/discussions)
- Email: srizd449@gmail.com

---

**See Also:**
- [PERFORMANCE.md](PERFORMANCE.md) - Speed optimization
- [SECURITY.md](SECURITY.md) - Security issues
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup issues
