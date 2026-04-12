# Performance Guide

Optimizing voria for speed and efficiency.

##  Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| CLI startup | < 2s | Before Python engine ready |
| Command response | < 100ms (p95) | After initial request |
| Simple issue fix | < 30s | Via LLM |
| Full automation | < 5min | For simple issues (1-2 iterations) |
| Token rate | < 1000/min | To avoid rate limiting |

##  Optimization Strategies

### 1. Disable Unnecessary Features

```bash
# Skip tests (if you know they pass)
voria issue 42 --skip-tests

# Dry run (don't modify files)
voria issue 42 --dry-run

# Single iteration (don't refine)
voria issue 42 --max-iterations 1
```

### 2. Use Fastest LLM Provider

**Speed Ranking** (fastest to slowest):
1. **Modal** - Sub-second responses (free!)
2. **Gemini** - 1-2 seconds
3. **OpenAI** - 2-3 seconds
4. **Claude** - 3-5 seconds

```bash
# Use fastest
voria issue 42 --llm modal
```

### 3. Cache Models

voria caches model responses. To warm up cache:

```bash
# Pre-download models
voria plan 1  # First time (slow)
voria plan 2  # Second time (faster - cached)
```

### 4. Parallel Operations

For batch processing:

```bash
# Process multiple issues in parallel
export voria_WORKERS=4
for issue in {1..20}; do
  voria issue $issue &
done
wait
```

### 5. Limit Context Size

Large codebases slow down analysis:

```bash
# Only analyze relevant files
voria issue 42 --include "src/api.py" --include "tests/test_api.py"

# Exclude large files
voria issue 42 --exclude "node_modules" --exclude "dist"
```

##  Profiling

### Python Profiling

```bash
# Run with timing
time python3 -m voria.engine < test_command.json

# Detailed profiling
python3 -m cProfile -s cumtime -m voria.engine < test_command.json
```

### Rust Profiling

```bash
# Flamegraph (Linux)
cargo install flamegraph
cargo flamegraph -- plan 1
# View: flamegraph.svg
```

##  Memory Usage

### Monitor Memory

```bash
# Watch memory usage
watch -n 1 'ps aux | grep voria'

# Detailed memory stats
/usr/bin/time -v ./target/release/voria plan 1
```

### Reduce Memory Footprint

```bash
# Smaller batch sizes
voria issue 42 --batch-size 100

# Disable caching
voria issue 42 --no-cache

# Limit context
voria issue 42 --max-files 10
```

##  Network Optimization

### Connection Pooling

voria reuses connections (built-in). To verify:

```python
# Check connection reuse
httpx.AsyncClient(limits=httpx.Limits(
    max_connections=5,        # Connection pool size
    max_keepalive_connections=5
))
```

### Rate Limiting

```bash
# Slow down token usage (avoid rate limits)
voria_TOKEN_RATE=100 voria issue 100  # 100 tokens/sec max

# Add delays between requests
voria_REQUEST_DELAY=2 voria issue 42  # 2 sec between requests
```

### DNS Caching

```python
# voria auto-caches DNS (via httpx)
# Verify with:
# strace -e openat ./target/release/voria plan 1 | grep hosts
```

##  Benchmarking

### Run Benchmarks

```bash
# Time different providers
for llm in modal openai gemini claude; do
  echo "Testing $llm..."
  time voria plan 1 --llm $llm
done

# Compare patch generation
for strategy in strict fuzzy; do
  echo "Testing $strategy..."
  time voria issue 1 --patch-strategy $strategy
done
```

### Create Benchmark Suite

```bash
# benchmark.sh
#!/bin/bash
ISSUES=(1 2 3 10 42 100)

for issue in "${ISSUES[@]}"; do
  echo "Issue #$issue"
  /usr/bin/time -f "%e seconds, %M KB" \
    ./target/release/voria plan $issue
done
```

##  LLM Token Optimization

### Use Smaller Models

```bash
# Smaller = faster + cheaper
voria issue 42 --llm modal              # GLM-5.1-FP8 (fast)
voria issue 42 --llm openai --model gpt-4.5-mini  # mini (faster)
voria issue 42 --llm claude --model claude-3-haiku  # haiku (fastest)
```

### Prompt Engineering

Keep prompts concise:

```python
# ❌ Slow: Large context
prompt = f"""Analyze this entire codebase:
{entire_codebase}
Fix {issue_description}
"""

# ✅ Fast: Focused context
prompt = f"""Analyze these files for {issue_description}:
{relevant_files_only}
"""
```

### Token Budget Awareness

```bash
# See token usage
voria plan 1 --verbose

# Output shows tokens consumed and cost
# Adjust budget if needed
python3 -m voria.core.setup  # Increase budget
```

##  Configuration Tuning

### Development Mode (Faster)

```bash
# Use debug builds (no optimizations)
cargo build          # vs cargo build --release

# Skip some validations
voria_SKIP_VALIDATION=1 ./target/debug/voria plan 1
```

### Production Mode (Slower but robust)

```bash
# Use release builds
cargo build --release

# With optimizations
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

##  Bottleneck Analysis

### Common Bottlenecks

1. **LLM API latency** (usually 2-5 seconds)
   - Switch to faster provider: `--llm modal`
   - Use smaller model: `--model gpt-4-mini`

2. **File I/O** (usually < 1 second)
   - Use faster disk (SSD vs HDD)
   - Exclude unnecessary files: `--exclude "*.log"`

3. **Test execution** (usually 10-30 seconds)
   - Skip tests: `--skip-tests`
   - Run subset: `--test-pattern "quick_*"`

4. **Git operations** (usually < 5 seconds)
   - Use shallow clone: `--shallow`
   - Skip fetch: `--no-fetch`

### Identify Bottleneck

```bash
# Add timing breakpoints
voria_DEBUG_TIMING=1 ./target/release/voria issue 42

# Output:
# [TIMING] LLM plan: 3.2s
# [TIMING] Patch generation: 2.1s
# [TIMING] File apply: 0.3s
# [TIMING] Test execution: 15.2s
# [TIMING] Total: 20.8s
```

##  Scaling

### Processing Many Issues

```bash
# Serial (slow)
for i in {1..100}; do
  voria issue $i --create-pr
done

# Parallel (faster)
seq 1 100 | parallel "voria issue {} --create-pr" --max-procs 4
```

### Load Balancing

```bash
# Distribute across LLM providers
for i in {1..100}; do
  llm=$((i % 4))  # Rotate: 0=modal, 1=openai, 2=gemini, 3=claude
  voria issue $i --llm ${LLMS[$llm]}
done
```

##  Performance Tips

1. **Use release builds** in production
2. **Keep local iteratons small** (-max-iterations 2-3)
3. **Enable caching** (default on, but verify)
4. **Use appropriate LLM** for task
5. **Focus on important files** (exclude boilerplate/tests)
6. **Monitor token spending** (avoid surprises)
7. **Reuse providers** (persistent process is faster)
8. **Batch operations** (parallel processing)

##  Advanced Tuning

### Rust Build Optimization

```bash
# Profile-guided optimization
RUSTFLAGS="-Cllvm-args=-pgo-warn-missing-function" cargo build --release -Z pgo=instrument

# High performance
RUSTFLAGS="-C opt-level=3 -C lto=yes -C codegen-units=1" cargo build --release
```

### Python Optimization

```python
# Use PyPy (faster than CPython)
pypy3 -m venv venv
source venv/bin/activate

# Compile to bytecode
python3 -m py_compile voria/
```

---

**See Also:**
- [SECURITY.md](SECURITY.md) - Security best practices
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

---

**Join our WhatsApp Support Group:** [Click Here](https://chat.whatsapp.com/IWude2099NAJmLTs8kgEuE?mode=gi_t)
