#!/usr/bin/env python3
"""
Victory Python Engine - AI Agent Loop

Communicates with Rust CLI via NDJSON over stdin/stdout.
- Reads: JSON commands from stdin
- Writes: JSON responses to stdout
- Logs: Debug/info to stderr
"""

import sys
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

# Configure logging to stderr only
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Track LLM token usage."""
    used: int = 0
    max: int = 0
    cost: float = 0.0


@dataclass
class Response:
    """NDJSON response message."""
    status: str  # success, pending, error
    action: str  # apply_patch, run_tests, continue, stop
    message: str
    patch: Optional[str] = None
    logs: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None


def send_response(response: Response) -> None:
    """Send NDJSON response to Rust CLI via stdout."""
    response_dict = asdict(response)
    # Remove None values
    response_dict = {k: v for k, v in response_dict.items() if v is not None}
    
    json_str = json.dumps(response_dict)
    sys.stdout.write(json_str + "\n")
    sys.stdout.flush()
    logger.debug(f"Response sent: {json_str}")


def handle_plan_command(command: Dict[str, Any]) -> None:
    """Handle 'plan' command to analyze issue without code changes."""
    issue_id = command.get("issue_id")
    iteration = command.get("iteration", 1)
    
    logger.debug(f"Processing plan command for issue #{issue_id} (iteration {iteration})")
    
    # Stub response - in real implementation, this would call LLM
    response = Response(
        status="success",
        action="stop",
        message=f"Plan generated for issue #{issue_id}",
    )
    send_response(response)


def handle_issue_command(command: Dict[str, Any]) -> None:
    """Handle 'issue' command to start full agent loop."""
    issue_id = command.get("issue_id")
    
    logger.debug(f"Processing issue command for issue #{issue_id}")
    
    response = Response(
        status="success",
        action="stop",
        message=f"Issue agent loop initialized for #{issue_id}",
    )
    send_response(response)


def handle_apply_command(command: Dict[str, Any]) -> None:
    """Handle 'apply' command to execute existing plan."""
    plan = command.get("plan")
    
    logger.debug(f"Processing apply command for plan: {plan}")
    
    response = Response(
        status="success",
        action="stop",
        message=f"Applied plan: {plan}",
    )
    send_response(response)


def handle_test_results_callback(command: Dict[str, Any]) -> None:
    """Handle test results callback from Rust."""
    test_status = command.get("test_status")
    test_logs = command.get("test_logs")
    
    logger.debug(f"Received test results: {test_status}")
    if test_logs:
        logger.debug(f"Test logs:\n{test_logs}")


def process_command(line: str) -> None:
    """Process a single NDJSON command line."""
    try:
        command = json.loads(line.strip())
        logger.debug(f"Command received: {command}")
        
        cmd_type = command.get("command")
        
        if cmd_type == "plan":
            handle_plan_command(command)
        elif cmd_type == "issue":
            handle_issue_command(command)
        elif cmd_type == "apply":
            handle_apply_command(command)
        elif cmd_type == "test_results":
            handle_test_results_callback(command)
        else:
            logger.error(f"Unknown command type: {cmd_type}")
            response = Response(
                status="error",
                action="stop",
                message=f"Unknown command: {cmd_type}",
            )
            send_response(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}", exc_info=True)
        response = Response(
            status="error",
            action="stop",
            message=f"Invalid JSON: {str(e)}",
        )
        send_response(response)
    except Exception as e:
        logger.error(f"Command processing error: {e}", exc_info=True)
        response = Response(
            status="error",
            action="stop",
            message=f"Processing error: {str(e)}",
        )
        send_response(response)


def main() -> None:
    """Main engine loop - read and process NDJSON from stdin."""
    logger.info("Victory Python Engine started")
    logger.info("Ready to receive commands via NDJSON on stdin")
    
    try:
        while True:
            line = sys.stdin.readline()
            
            # EOF or empty line
            if not line:
                logger.info("Received EOF, shutting down")
                break
            
            # Process the command
            process_command(line)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Victory Python Engine shutting down")


if __name__ == "__main__":
    main()
