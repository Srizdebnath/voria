# Examples

Real-world examples of using Victory to fix open source issues.

##  Example 1: Simple Bug Fix

### Scenario
A simple bug in a Python library where a function returns wrong type.

### Command
```bash
victory issue 42
```

### What Happens

1. **Fetch Issue**
   ```
   Issue #42: TypeError in calculate_total()
   Description: When given empty list, returns None instead of 0
   ```

2. **Plan**
   ```
   Detected: Simple return value bug
   Plan: Add condition to return 0 for empty input
   Estimated effort: 5 minutes
   ```

3. **Generate Patch**
   ```diff
   -def calculate_total(items):
   +def calculate_total(items):
   +    if not items:
   +        return 0
        return sum(items)
   ```

4. **Test**
   ```
   Running pytest...
   ✓ All 12 tests pass
   ✓ New test cases pass
   ```

5. **Result**
   ```
   ✅ Issue fixed!
   Pull Request created: #1234
   ```

##  Example 2: Feature Implementation with Iteration

### Scenario
Adding a new feature that requires multiple iterations to get tests passing.

### Command
```bash
victory issue 100 --verbose --max-iterations 5
```

### Iteration Details

**Iteration 1:**
- Plan: Add new `filter()` method
- Patch: Adds basic filter implementation
- Test: FAILED - Missing parameter validation

**Iteration 2:**
- Analysis: Tests expect validation error
- Patch: Add parameter type checking
- Test: FAILED - Missing docstring

**Iteration 3:**
- Analysis: Linting checks require docs
- Patch: Add docstring and examples
- Test: PASSED ✓

Result: Feature ready after 3 iterations

##  Example 3: Complex Multi-File Change

### Scenario
API migration requiring changes across 5+ files.

### Command
```bash
victory issue 200 --dry-run --verbose
```

### Dry Run Output
```
Would modify:
  ✓ src/api.py (3 changes)
  ✓ src/models.py (2 changes)
  ✓ tests/test_api.py (5 changes)
  ✓ docs/api.md (1 change)
  ✓ setup.py (1 change)

Would run tests:
  ✓ pytest tests/ (estimated 2m)
  ✓ Coverage report (estimated 30s)

Estimated impact:
  - Lines added: 120
  - Lines removed: 85
  - Files modified: 5
```

**After verification:**
```bash
victory issue 200 --create-pr
```

## 🧪 Example 4: Using Different LLM Providers

### Compare LLMs

**Modal (Fastest, Free)**
```bash
victory issue 50 --llm modal --verbose
Time: 2 minutes
Cost: $0
Result: Works but basic
```

**OpenAI GPT-5.4 (Best Quality)**
```bash
victory issue 50 --llm openai --verbose
Time: 5 minutes
Cost: $0.15
Result: Excellent, well-documented
```

**Google Gemini (Best Balance)**
```bash
victory issue 50 --llm gemini --verbose
Time: 3 minutes
Cost: $0.05
Result: Good quality, fast
```

##  Example 5: Custom Test Command

### Scenario
Repository uses custom test framework (not auto-detected).

### Setup
```bash
victory issue 75 --test-cmd "npm run test:coverage" --test-pattern "*.test.js"
```

### What Happens
1. Generates patch
2. Applies patch
3. Runs: `npm run test:coverage`
4. Parses custom coverage output
5. Determines success/failure
6. Iterates if needed

##  Example 6: Code Quality Issues

### Scenario
Issue about code formatting/linting violations.

### Command
```bash
victory issue 15 --hook "pre-test: black src/ && pylint src/"
```

### Workflow
1. Plan: Identify formatting needed
2. Patch: Generate fixes
3. Apply patch
4. Pre-test: Run black formatter + pylint
5. Test: Run test suite
6. Success: Clean code + passing tests

##  Example 7: Documentation Update

### Scenario
GitHub issue requesting documentation improvements.

### Command
```bash
victory issue 88 --save-iterations --output markdown
```

### Result: Markdown Report
```markdown
# Issue #88: Fix Documentation

## Plan
Add examples and API reference for new module

## Changes Made
- Added quickstart guide
- Added 5 practical examples
- Updated API documentation
- Added troubleshooting section

## Test Results
- ✅ All documentation builds successfully
- ✅ Links are valid
- ✅ Code examples run without errors
```

##  Example 8: Security-Related Fix

### Scenario
Security vulnerability that needs careful handling.

### Command
```bash
victory issue 300 \
  --require-approval \
  --skip-auto-pr \
  --save-analysis \
  --verbose
```

### Output
```
[SECURITY] Analyzing vulnerability...
Identified: SQL injection in user input handling
Severity: HIGH

Generated fix:
✓ Adds parameterized queries
✓ Adds input validation
✓ Adds security tests

Awaiting approval before:
- Applying patch
- Running tests
- Creating PR

Review: ./analysis/issue-300-security-review.md
```

##  Example 9: Performance Optimization

### Scenario
Issue about slow function that needs optimization.

### Command
```bash
victory issue 42 \
  --test-cmd "pytest benchmarks/" \
  --performance-baseline 2.5s \
  --verbose
```

### Workflow
1. Plan: Identify optimization opportunity
2. Generate: Optimize algorithm/caching
3. Benchmark: `pytest benchmarks/` shows 0.8s (3x faster!)
4. Test: All tests pass
5. Success: "30% performance improvement"

##  Example 10: Batch Processing Multiple Issues

### Scenario
Fix multiple related issues at once.

### Script
```bash
#!/bin/bash
ISSUES=(42 43 44 45 46)
for issue in "${ISSUES[@]}"; do
  echo "Processing issue #$issue..."
  victory issue $issue --create-pr --llm gemini
  sleep 2  # Rate limiting
done
```

### Output
```
Processing issue #42...
✅ Created PR #1234

Processing issue #43...
✅ Created PR #1235

Processing issue #44...
✅ Created PR #1236

...

All issues processed! 5 PRs created.
```

##  Example 11: Investigating Before Fixing

### Scenario
Complex issue - want to analyze before fixing.

### Commands
```bash
# Step 1: Just plan
victory plan 999 --verbose

# Step 2: Dry run
victory issue 999 --dry-run

# Step 3: Dry run with specific LLM
victory issue 999 --dry-run --llm claude

# Step 4: Dry run with custom tests
victory issue 999 --dry-run --test-cmd "npm run test:all"

# Step 5: Actually run it
victory issue 999 --create-pr
```

##  Example 12: Handling Failures

### Scenario
Fix attempt fails - how to debug and retry.

### Commands
```bash
# First attempt
victory issue 50 --verbose

# If it fails, review logs
victory logs issue 50 --level DEBUG

# Try with different LLM
victory issue 50 --llm claude

# Or with higher iterations
victory issue 50 --max-iterations 8

# Or manually fix and apply
victory apply manual-plan
```

##  Example 13: Progress Monitoring

### Scenario
Monitor Victory's progress on an issue.

### Commands
```bash
# Terminal 1: Start Victory
victory issue 42 --verbose --follow-logs

# Terminal 2: Monitor status
while true; do
  victory status issue 42
  sleep 5
done

# Terminal 3: Check token usage
watch victory token info
```

##  Example 14: GitHub Enterprise Integration

### Scenario
Using Victory with GitHub Enterprise (on-premise).

### Setup
```bash
# Configure GitHub Enterprise
python3 -m victory.core.setup

# Select: github-enterprise
# Enter: https://github.enterprise.com
# Token: ghp_...
```

### Usage
```bash
victory issue 42 --github https://github.enterprise.com
```

##  Best Practice: The Complete Workflow

### Full Workflow Example
```bash
# 1. Investigate
victory plan 42 --verbose

# 2. Dry run (no modifications)
victory issue 42 --dry-run --verbose

# 3. Check what changed (before applying)
victory logs issue 42 --dry-run

# 4. Run with minimal risk
victory issue 42 \
  --max-iterations 3 \
  --require-approval \
  --save-analysis

# 5. If successful, create PR
victory issue 42 --create-pr

# 6. Monitor the PR
victory status pr-id

# 7. Review results
victory logs issue 42 --output markdown > review.md
```

##  Learning from Examples

**Run the Examples:**
```bash
# Try all examples in sequence
for ex in {1..5}; do
  echo "Running example $ex..."
  victory example $ex --verbose
done
```

**Understand the Output:**
```bash
# Generate detailed analysis
victory issue 42 --output json | jq . | less

# Export to markdown
victory issue 42 --output markdown > report.md

# Compare different approaches
diff <(victory issue 42 --llm openai --output json) \
     <(victory issue 42 --llm modal --output json)
```

---

**Try these examples!** Start with simplest (Example 1) and work up to more complex ones.
