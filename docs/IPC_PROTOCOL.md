# IPC Protocol Specification

## Overview

Victory uses **NDJSON** (newline-delimited JSON) for inter-process communication between the Rust CLI and Python engine.

## Format Rules (MANDATORY)

1. **One JSON object per line** - no line wrapping
2. **Newline terminator** - exactly `\n` after each JSON object
3. **No multi-line JSON** - protocol messages must fit on single line
4. **Flush after write** - must call `flush()` immediately after writing
5. **Line-by-line reading** - read one complete line at a time

### Example

```
{"command":"plan","issue_id":1}\n
{"status":"success","action":"stop","message":"Done"}\n
```

NOT acceptable:
```
{"command":"plan",
"issue_id":1}
```

## Stdout/Stderr Discipline

### Python Side

**stdout** (ONLY protocol messages):
```python
response = {"status": "success", "action": "stop", "message": "Done"}
print(json.dumps(response))  # Automatic \n added
sys.stdout.flush()           # CRITICAL!
```

**stderr** (logs and debug info):
```python
logger.info("Processing issue...")        # Goes to stderr
logger.debug("Token count: 1000")          # Goes to stderr
print(f"Debug: {value}", file=sys.stderr) # Goes to stderr
```

### Rust Side

**Reads**: Only from stdout (line-by-line JSON parsing)
**Pipes**: stderr directly to user console

## Message Types

### Request (Rust → Python)

Sent by Rust CLI to invoke Python processing.

```json
{
  "command": "plan|issue|apply|graph|test_results",
  "issue_id": 123,
  "repo_path": "/path/to/repo",
  "iteration": 1,
  "extra_field": "optional"
}
```

**Fields**:
- `command` (required): The action to perform
- `issue_id` (optional): GitHub issue number
- `repo_path` (optional): Local repository path
- `iteration` (optional): Loop iteration count (1-5)

**Command Types**:
- `plan`: Analyze issue without code changes
- `issue`: Start full agent loop
- `apply`: Execute a previously generated plan
- `graph`: Generate dependency graph
- `test_results`: Callback with test results

### Response (Python → Rust)

Sent by Python engine to Rust CLI after processing.

```json
{
  "status": "success|pending|error",
  "action": "apply_patch|run_tests|continue|stop",
  "message": "Human-readable status message",
  "patch": "... unified diff format ...",
  "logs": "... multi-line debug output ...",
  "token_usage": {
    "used": 1000,
    "max": 4000,
    "cost": 0.05
  }
}
```

**Fields**:
- `status` (required): Success, pending work, or error
- `action` (required): What Rust should do next
- `message` (required): Human-readable message
- `patch` (optional): Unified diff format patch
- `logs` (optional): Multi-line debug logs
- `token_usage` (optional): LLM token accounting

**Status Values**:
- `success`: Action completed successfully
- `pending`: Action in progress, expect more messages
- `error`: Action failed with error

**Action Values**:
- `apply_patch`: Apply the patch to filesystem
- `run_tests`: Execute test suite
- `continue`: Continue to next iteration
- `stop`: Stop processing, issue is done

### Callback (Rust → Python)

Sent by Rust to inform Python of execution results.

```json
{
  "command": "test_results",
  "test_status": "passed|failed",
  "test_logs": "... test output ...",
  "error": "... error message if failed ..."
}
```

**Fields**:
- `command` (required): `test_results`
- `test_status` (required): passed or failed
- `test_logs` (optional): Test suite output
- `error` (optional): Error message if failed

## Protocol Flow Examples

### Example 1: Simple Plan Request

```
RUST → PYTHON:
{"command":"plan","issue_id":1,"iteration":1}

PYTHON → RUST:
{"status":"success","action":"stop","message":"Plan generated for issue #1"}
```

### Example 2: Full Agent Loop

```
RUST → PYTHON:
{"command":"issue","issue_id":123,"repo_path":"/home/user/repo"}

PYTHON → RUST:
{"status":"pending","action":"apply_patch","message":"Generated patch","patch":"--- a/src/main.py\n+++ b/src/main.py\n@@ -1,3 +1,3 @@\n..."}

RUST applies patch, runs tests

RUST → PYTHON:
{"command":"test_results","test_status":"failed","test_logs":"..."}

PYTHON → RUST:
{"status":"pending","action":"continue","message":"Tests failed, refining..."}

... (iterations) ...

PYTHON → RUST:
{"status":"success","action":"stop","message":"Issue resolved!"}
```

### Example 3: Error Handling

```
RUST → PYTHON:
{"command":"plan","issue_id":1}

PYTHON → RUST:
{"status":"error","action":"stop","message":"Failed to fetch issue: API key missing","logs":"...traceback..."}

RUST displays error and exits
```

## Encoding

- **Character Encoding**: UTF-8
- **JSON Spec**: RFC 7159
- **Line Terminator**: LF (`\n`) on Unix/Linux/macOS, CRLF (`\r\n`) OK but LF preferred

## Timeout Behavior

### Rust Timeout Detection

If no response received for 30 seconds:

1. Log timeout message
2. Kill Python subprocess
3. Restart Python engine
4. Retry last request once
5. If still no response after 30s → exit with error

### Python Timeout Prevention

Python should send a response within reasonable time (< 5s for most operations).

For long operations:
- Send periodic `pending` messages
- Or implement streaming (future enhancement)

## Error Handling

### Python Errors

If Python encounters an error processing a request:

```json
{
  "status": "error",
  "action": "stop",
  "message": "Description of what failed",
  "logs": "... traceback to stderr ..."
}
```

### Rust Errors

If Rust encounters an error:

1. Log the error
2. Skip to next command
3. Or restart Python if critical

### JSON Parse Errors

If either side receives invalid JSON:

1. Log the error to stderr
2. Send error response if possible
3. Or abort current operation

## Performance Guidelines

- **Parse Speed**: NDJSON parsing should be < 1ms per message
- **Flush Timing**: Flush within 100ms of write
- **Message Size**: Keep messages < 1MB (practical limit)
- **Latency**: Aim for < 100ms roundtrip for simple operations

## Versioning

Current protocol version: **1.0**

Protocol changes require coordination between Rust and Python versions.

## Testing

### Manual Test (Python Engine)

```bash
echo '{"command":"plan","issue_id":1}' | python3 -m victory.engine
```

Expected output:
```
{"status":"success","action":"stop","message":"Plan generated for issue #1"}
```

### Manual Test (Full CLI)

```bash
./target/debug/victory -v plan 1
```

Expected behavior:
- [i] Planning fix for issue #1
- [✓] Plan generated for issue #1
- Process exits cleanly

## Debugging

Enable verbose logging:

```bash
RUST_LOG=debug ./target/debug/victory plan 1
```

This shows:
- JSON being sent to Python
- JSON being received from Python
- Timing information
- Process lifecycle events

View Python logs:

```bash
./target/debug/victory -v plan 1 2>&1 | grep -E "\[DEBUG\]|\[INFO\]"
```

## Backward Compatibility

Currently no versioning mechanism. Once protocol is stable, add version field:

```json
{
  "version": "1.0",
  "command": "...",
  ...
}
```
