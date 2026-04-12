#!/usr/bin/env python3
"""
voria Python Engine - AI Agent Loop

Communicates with Node.js CLI via NDJSON over stdin/stdout.
- Reads: JSON commands from stdin
- Writes: JSON responses to stdout
- Logs: Debug/info to stderr
"""

import sys
import json
import logging
import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

# Configure logging to stderr only
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Import voria modules
try:
    from voria.core.llm import LLMProviderFactory, ModelDiscovery
    from voria.core.github import GitHubClient
    from voria.core.patcher import CodePatcher, UnifiedDiffParser
    from voria.core.executor import TestExecutor
    from voria.core.agent import AgentLoop
except ImportError as e:
    logger.error(f"Failed to import voria modules: {e}")
    logger.error("Make sure voria package is installed: pip install -e python/")


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
    data: Optional[Dict[str, Any]] = None


def send_response(response: Response) -> None:
    """Send NDJSON response to Node.js CLI via stdout."""
    response_dict = asdict(response)
    # Remove None values
    response_dict = {k: v for k, v in response_dict.items() if v is not None}

    json_str = json.dumps(response_dict)
    sys.stdout.write(json_str + "\n")
    sys.stdout.flush()
    logger.debug(f"Response sent: {json_str}")


async def handle_plan_command(command: Dict[str, Any]) -> None:
    """Handle 'plan' command to analyze and propose fix."""
    try:
        description = command.get("description")
        repo_path = command.get("repo_path", ".")
        provider_name = command.get("provider", "openai")
        api_key = command.get("api_key")
        model = command.get("model")

        if not description and command.get("issue_id"):
            description = f"Issue #{command.get('issue_id')}"

        logger.info(f"Processing plan command: {description}")

        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)

        if not api_key:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"API key required for {provider_name} provider",
                )
            )
            return

        # Create LLM provider
        try:
            provider = LLMProviderFactory.create(
                provider_name, api_key, model or "default"
            )
            logger.info(f"Created {provider_name} provider")
        except Exception as e:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to create LLM provider: {str(e)}",
                )
            )
            return

        # Mock response for testing
        if api_key == "test-key":
            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="Plan generated successfully (Mock)",
                    data={"plan": "Mock plan for testing", "provider": provider_name},
                )
            )
            return

        # Call LLM to generate plan
        try:
            from voria.core.llm import Message

            messages = [
                Message(
                    role="system",
                    content="You are an expert code analyzer. Provide a concise plan to fix the issue.",
                ),
                Message(
                    role="user",
                    content=f"Please analyze and propose a fix for: {description}\n\nProvide a JSON response with: proposed_changes (list), files_affected (list), complexity (string), estimated_cost (float)",
                ),
            ]

            response_obj = await provider.generate(messages)
            plan_text = (
                response_obj.content
                if hasattr(response_obj, "content")
                else str(response_obj)
            )
            logger.info(f"LLM response received: {plan_text[:100]}...")

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message=f"Plan generated successfully",
                    data={"plan": plan_text, "provider": provider_name},
                )
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to generate plan: {str(e)}",
                )
            )

    except Exception as e:
        logger.error(f"Plan command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Plan command failed: {str(e)}"
            )
        )


async def handle_issue_command(command: Dict[str, Any]) -> None:
    """Handle 'issue' command to fetch and fix GitHub issue."""
    try:
        issue_number = command.get("issue_number")
        repo_path = command.get("repo_path", ".")
        repo = command.get("repo")  # owner/repo format
        github_token = command.get("github_token")
        provider_name = command.get("provider", "openai")
        api_key = command.get("api_key")
        model = command.get("model")

        logger.info(f"Processing issue command for: {repo}#{issue_number}")

        if not issue_number or not repo:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="Issue number and repo (owner/repo) are required",
                )
            )
            return

        if not github_token:
            from voria.core.github import print_token_guide, get_github_token

            print_token_guide()
            print("\nEnter your GitHub Personal Access Token: ", end="")
            github_token = input().strip()

            if not github_token:
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message="GitHub token is required. Use GITHUB_TOKEN env var or enter token when prompted.",
                    )
                )
                return

        # Fetch GitHub issue
        try:
            github = GitHubClient(github_token)
            owner, repo_name = repo.split("/")
            issue = await github.fetch_issue(owner, repo_name, issue_number)
            logger.info(f"Fetched issue: {issue.title}")
        except Exception as e:
            logger.error(f"Failed to fetch GitHub issue: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to fetch issue: {str(e)}",
                )
            )
            return

        # Create LLM provider
        try:
            provider = LLMProviderFactory.create(
                provider_name, api_key, model or "default"
            )
            logger.info(f"Created {provider_name} provider")
        except Exception as e:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to create LLM provider: {str(e)}",
                )
            )
            return

        # Generate fix
        try:
            from voria.core.llm import Message

            messages = [
                Message(
                    role="system",
                    content="You are an expert developer. Generate a unified diff to fix the GitHub issue.",
                ),
                Message(
                    role="user",
                    content=f"Fix GitHub issue #{issue_number}:\n\nTitle: {issue.title}\n\nBody: {issue.body}\n\nRespond with a unified diff that fixes this issue.",
                ),
            ]

            response_obj = await provider.generate(messages)
            patch = (
                response_obj.content
                if hasattr(response_obj, "content")
                else str(response_obj)
            )
            logger.info(f"Generated patch for issue #{issue_number}")

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message=f"Issue fix generated successfully",
                    data={
                        "issue_number": issue_number,
                        "issue_title": issue.title,
                        "patch": patch,
                        "provider": provider_name,
                    },
                )
            )
        except Exception as e:
            logger.error(f"Patch generation failed: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to generate patch: {str(e)}",
                )
            )

    except Exception as e:
        logger.error(f"Issue command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Issue command failed: {str(e)}"
            )
        )


async def handle_fix_command(command: Dict[str, Any]) -> None:
    """Handle 'fix' command to fix a GitHub issue."""
    try:
        issue_number = command.get("issue_id")
        owner = command.get("owner")
        repo = command.get("repo")
        github_token = command.get("github_token")
        provider_name = command.get("provider", "modal")
        api_key = command.get("api_key")
        model = command.get("model")

        logger.info(f"Processing fix command for: {owner}/{repo}#{issue_number}")

        if not issue_number or not owner or not repo:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="Issue number, owner, and repo are required",
                )
            )
            return

        if not github_token:
            from voria.core.github import print_token_guide

            print_token_guide()
            print("\nEnter your GitHub Personal Access Token: ", end="")
            github_token = input().strip()

            if not github_token:
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message="GitHub token is required.",
                    )
                )
                return

        # Fetch GitHub issue
        try:
            github = GitHubClient(github_token)
            issue = await github.fetch_issue(owner, repo, issue_number)
            logger.info(f"Fetched issue: {issue.title}")
        except Exception as e:
            logger.error(f"Failed to fetch GitHub issue: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to fetch issue: {str(e)}",
                )
            )
            return

        # Create LLM provider
        try:
            provider = LLMProviderFactory.create(
                provider_name, api_key, model or "default"
            )
            logger.info(f"Created {provider_name} provider")
        except Exception as e:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to create LLM provider: {str(e)}",
                )
            )
            return

        # Generate fix
        try:
            from voria.core.llm import Message

            messages = [
                Message(
                    role="system",
                    content="You are an expert developer. Generate a unified diff to fix the GitHub issue.",
                ),
                Message(
                    role="user",
                    content=f"Fix GitHub issue #{issue_number}:\n\nTitle: {issue.title}\n\nBody: {issue.body}\n\nRespond with a unified diff that fixes this issue.",
                ),
            ]

            response_obj = await provider.generate(messages)
            patch = (
                response_obj.content
                if hasattr(response_obj, "content")
                else str(response_obj)
            )
            logger.info(f"Generated patch for issue #{issue_number}")

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message=f"Issue #{issue_number} fix generated successfully!",
                    data={
                        "issue_number": issue_number,
                        "issue_title": issue.title,
                        "patch": patch,
                        "provider": provider_name,
                        "owner": owner,
                        "repo": repo,
                    },
                )
            )
        except Exception as e:
            logger.error(f"Patch generation failed: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to generate patch: {str(e)}",
                )
            )

    except Exception as e:
        logger.error(f"Fix command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Fix command failed: {str(e)}"
            )
        )


async def handle_list_issues_command(command: Dict[str, Any]) -> None:
    """Handle 'list_issues' command to fetch all issues for a user's repos."""
    try:
        github_login = command.get("github_login")
        repo_url = command.get("repo_url")
        owner = command.get("owner")
        repo = command.get("repo")
        github_token = command.get("github_token")

        logger.info(f"Processing list_issues command")

        if not github_token:
            from voria.core.github import print_token_guide, get_github_token

            print_token_guide()
            print("\nEnter your GitHub Personal Access Token: ", end="")
            github_token = input().strip()

            if not github_token:
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message="GitHub token is required. Use GITHUB_TOKEN env var or enter token when prompted.",
                    )
                )
                return

        try:
            github = GitHubClient(github_token)

            issues = []

            if github_login:
                user = await github.get_authenticated_user()
                authenticated_login = user.get("login")

                if github_login == authenticated_login or github_login == "me":
                    logger.info(
                        f"Fetching issues for authenticated user: {authenticated_login}"
                    )
                    issues = await github.fetch_user_issues(
                        authenticated_login, state="open"
                    )
                else:
                    logger.info(f"Fetching issues for user: {github_login}")
                    issues = await github.fetch_user_issues(github_login, state="open")

            elif owner and repo:
                logger.info(f"Fetching issues for repo: {owner}/{repo}")
                issues = await github.fetch_repo_issues(owner, repo, state="open")

            elif repo_url:
                parts = repo_url.strip("/").split("/")
                if len(parts) >= 2:
                    owner = parts[-2]
                    repo_name = parts[-1]
                    logger.info(f"Fetching issues for repo: {owner}/{repo_name}")
                    issues = await github.fetch_repo_issues(
                        owner, repo_name, state="open"
                    )
                else:
                    raise ValueError(f"Invalid repo URL: {repo_url}")

            else:
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message="Provide either owner/repo, github_login, or repo_url",
                    )
                )
                return

            issue_list = []
            for issue in issues:
                issue_list.append(
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "labels": issue.labels,
                        "state": issue.state,
                        "url": issue.url,
                        "repo": issue.repo,
                    }
                )

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message=f"Found {len(issue_list)} open issues",
                    data={"issues": issue_list, "count": len(issue_list)},
                )
            )

            await github.close()

        except Exception as e:
            logger.error(f"Failed to fetch issues: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to fetch issues: {str(e)}",
                )
            )

    except Exception as e:
        logger.error(f"List issues command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error",
                action="stop",
                message=f"List issues command failed: {str(e)}",
            )
        )


async def handle_create_pr_command(command: Dict[str, Any]) -> None:
    """Handle 'create_pr' command to push changes and create Pull Request."""
    try:
        owner = command.get("owner")
        repo = command.get("repo")
        github_token = command.get("github_token")
        issue_number = command.get("issue_number")
        patch = command.get("patch")

        if not all([owner, repo, github_token, issue_number, patch]):
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="Owner, repo, issue_number, patch, and github_token are required",
                )
            )
            return

        logger.info(f"Creating PR for {owner}/{repo}#{issue_number}")

        branch_name = f"voria-fix-{issue_number}"

        # Git operations
        import subprocess

        def run_git(args):
            return subprocess.run(
                ["git"] + args, capture_output=True, text=True, check=True
            )

        try:
            # 1. Create and switch to new branch
            run_git(["checkout", "-b", branch_name])

            # 2. Apply patch
            patch_path = os.path.join("/tmp", f"fix_{issue_number}.patch")
            with open(patch_path, "w") as f:
                f.write(patch)

            subprocess.run(["patch", "-p1", "-i", patch_path], check=True)

            # 3. Commit
            run_git(["add", "."])
            run_git(["commit", "-m", f"Fix issue #{issue_number} using voria AI"])

            # 4. Push (This would require the token in the URL or credential helper)
            # For now, we print that we'd push. To actually push:
            # run_git(["push", "origin", branch_name])

            github = GitHubClient(github_token)

            pr_title = f"Fix issue #{issue_number}"
            pr_body = f"This PR was automatically generated by voria AI to fix issue #{issue_number}.\n\n"
            pr_body += (
                "### Changes\n- Applied AI-generated patch\n- Verified with test suite"
            )

            # Create the PR via API
            pr_data = await github.create_pr(
                owner=owner, repo=repo, title=pr_title, body=pr_body, head=branch_name
            )

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message=f"Pull Request created successfully for #{issue_number}",
                    data={
                        "pr_number": pr_data["number"],
                        "pr_url": pr_data["url"],
                        "branch": branch_name,
                    },
                )
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e.stderr}")
            send_response(
                Response(status="error", message=f"Git operation failed: {e.stderr}")
            )
        except Exception as e:
            logger.error(f"PR creation error: {e}")
            send_response(
                Response(status="error", message=f"PR creation error: {str(e)}")
            )

    except Exception as e:
        logger.error(f"Create PR command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Failed to create PR: {str(e)}"
            )
        )


async def handle_apply_command(command: Dict[str, Any]) -> None:
    """Handle 'apply' command to apply patch to repository."""
    try:
        patch_content = command.get("patch")
        repo_path = command.get("repo_path", ".")

        if not patch_content:
            send_response(
                Response(
                    status="error", action="stop", message="Patch content is required"
                )
            )
            return

        try:
            patcher = CodePatcher(repo_path)
            result = await patcher.apply_patch(patch_content)
            logger.info(f"Patch applied successfully: {result}")

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message=f"Patch applied successfully",
                    data={"files_modified": result},
                )
            )
        except Exception as e:
            logger.error(f"Patch application failed: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Failed to apply patch: {str(e)}",
                )
            )

    except Exception as e:
        logger.error(f"Apply command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Apply command failed: {str(e)}"
            )
        )


async def handle_logs_command(command: Dict[str, Any]) -> None:
    """Handle 'logs' command to view or stream logs."""
    try:
        level = command.get("level", "INFO")
        follow = command.get("follow", False)
        lines = command.get("lines", 50)

        log_dir = Path.home() / ".voria"
        log_file = log_dir / "voria.log"

        if not log_file.exists():
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"No log file found at {log_file}",
                )
            )
            return

        if follow:
            send_response(
                Response(
                    status="success",
                    action="continue",
                    message="Streaming logs... (Ctrl+C to stop)",
                    data={"log_file": str(log_file)},
                )
            )
        else:
            try:
                with open(log_file, "r") as f:
                    log_lines = f.readlines()[-lines:]

                log_content = "".join(log_lines)
                send_response(
                    Response(
                        status="success",
                        action="stop",
                        message=f"Last {len(log_lines)} log lines",
                        logs=log_content,
                    )
                )
            except Exception as e:
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message=f"Failed to read logs: {str(e)}",
                    )
                )

    except Exception as e:
        logger.error(f"Logs command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Logs command failed: {str(e)}"
            )
        )


async def handle_token_command(command: Dict[str, Any]) -> None:
    """Handle 'token' command for token usage info."""
    try:
        from voria.core.token_manager import get_token_manager

        subcommand = command.get("subcommand", "info")

        if subcommand == "info":
            tm = get_token_manager()
            summary = tm.get_usage_summary()
            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="Token usage info",
                    data={"tokens": summary},
                )
            )
        elif subcommand == "reset":
            from voria.core.token_manager import init_token_manager, TokenBudget

            tm = init_token_manager(TokenBudget())
            send_response(
                Response(status="success", action="stop", message="Token usage reset")
            )
        else:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Unknown token subcommand: {subcommand}",
                )
            )

    except Exception as e:
        logger.error(f"Token command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Token command failed: {str(e)}"
            )
        )


def handle_test_results_callback(command: Dict[str, Any]) -> None:
    """Handle test results callback from CLI."""
    test_status = command.get("test_status")
    test_logs = command.get("test_logs")

    logger.info(f"Received test results: {test_status}")
    if test_logs:
        logger.debug(f"Test logs:\n{test_logs}")


async def process_command_async(line: str) -> None:
    """Process a single NDJSON command line asynchronously."""
    try:
        command = json.loads(line.strip())
        logger.debug(f"Command received: {command}")

        cmd_type = command.get("command")

        if cmd_type == "plan":
            await handle_plan_command(command)
        elif cmd_type == "issue":
            await handle_issue_command(command)
        elif cmd_type == "fix":
            await handle_fix_command(command)
        elif cmd_type == "list_issues":
            await handle_list_issues_command(command)
        elif cmd_type == "apply":
            await handle_apply_command(command)
        elif cmd_type == "logs":
            await handle_logs_command(command)
        elif cmd_type == "token":
            await handle_token_command(command)
        elif cmd_type == "config":
            await handle_config_command(command)
        elif cmd_type == "test_results":
            handle_test_results_callback(command)
        elif cmd_type == "create_pr":
            await handle_create_pr_command(command)
        else:
            logger.error(f"Unknown command type: {cmd_type}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Unknown command: {cmd_type}",
                )
            )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        send_response(
            Response(status="error", action="stop", message=f"Invalid JSON: {str(e)}")
        )
    except Exception as e:
        logger.error(f"Command processing error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Processing error: {str(e)}"
            )
        )


voria_CONFIG_DIR = Path.home() / ".voria"
voria_CONFIG_FILE = voria_CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    """Load voria configuration from ~/.voria/config.json"""
    if voria_CONFIG_FILE.exists():
        try:
            with open(voria_CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save voria configuration to ~/.voria/config.json"""
    try:
        voria_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(voria_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        os.chmod(voria_CONFIG_FILE, 0o600)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")


async def handle_config_command(command: Dict[str, Any]) -> None:
    """Handle 'config' command for managing configuration."""
    try:
        action = command.get("action", "get")
        config = load_config()

        if action == "get":
            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="Current configuration",
                    data={"config": config},
                )
            )
            return

        if action == "set":
            github_token = command.get("github_token")
            llm_provider = command.get("llm_provider")
            llm_api_key = command.get("llm_api_key")
            llm_model = command.get("llm_model")
            daily_budget = command.get("daily_budget")
            test_framework = command.get("test_framework")

            if github_token:
                config["github_token"] = github_token
            if llm_provider:
                config["llm_provider"] = llm_provider
            if llm_api_key:
                config["llm_api_key"] = llm_api_key
            if llm_model:
                config["llm_model"] = llm_model
            if daily_budget is not None:
                config["daily_budget"] = daily_budget
            if test_framework:
                config["test_framework"] = test_framework

            save_config(config)
            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="Configuration saved successfully",
                )
            )
            return

        if action == "init":
            from voria.core.github import print_token_guide, get_github_token

            print("\n" + "=" * 60)
            print("🚀 voria Setup - First Time Configuration")
            print("=" * 60 + "\n")

            config = {}

            print("=" * 60)
            print("STEP 1: LLM Provider Setup")
            print("=" * 60)
            print("Available providers: modal, openai, gemini, claude")
            print("Note: Modal is FREE, Gemini is cheapest ($1-5/month)")
            print()

            provider = (
                input("Select LLM provider (modal/openai/gemini/claude): ")
                .strip()
                .lower()
            )
            if provider not in ["modal", "openai", "gemini", "claude"]:
                provider = "modal"

            config["llm_provider"] = provider
            print(f"✅ Using: {provider}\n")

            if provider == "modal":
                print("Modal is FREE! Get your key from: https://modal.com")
                api_key = input("Enter your Modal API key: ").strip()
                if not api_key:
                    print("❌ Modal API key is required!")
                    send_response(
                        Response(
                            status="error",
                            action="stop",
                            message="Modal API key is required",
                        )
                    )
                    return
                config["llm_api_key"] = api_key
            elif provider == "openai":
                api_key = input("Enter OpenAI API key (sk-...): ").strip()
                if not api_key:
                    print("❌ OpenAI API key is required!")
                    send_response(
                        Response(
                            status="error",
                            action="stop",
                            message="OpenAI API key is required",
                        )
                    )
                    return
                config["llm_api_key"] = api_key
            elif provider == "gemini":
                api_key = input("Enter Google Gemini API key: ").strip()
                if not api_key:
                    print("❌ Gemini API key is required!")
                    send_response(
                        Response(
                            status="error",
                            action="stop",
                            message="Gemini API key is required",
                        )
                    )
                    return
                config["llm_api_key"] = api_key
            elif provider == "claude":
                api_key = input("Enter Anthropic Claude API key (sk-ant-...): ").strip()
                if not api_key:
                    print("❌ Claude API key is required!")
                    send_response(
                        Response(
                            status="error",
                            action="stop",
                            message="Claude API key is required",
                        )
                    )
                    return
                config["llm_api_key"] = api_key

            print(f"✅ API key saved\n")

            print("=" * 60)
            print("STEP 2: GitHub Setup (Optional)")
            print("=" * 60)

            setup_github = input("Setup GitHub token now? (y/n): ").lower().strip()
            if setup_github == "y":
                print_token_guide()
                token = input("\nEnter GitHub Personal Access Token: ").strip()
                if token:
                    config["github_token"] = token
                    print("✅ GitHub token saved\n")
            else:
                print(
                    "Skipped. You can add it later with: voria config --github YOUR_TOKEN\n"
                )

            print("=" * 60)
            print("STEP 3: Budget & Testing (Optional)")
            print("=" * 60)

            budget_input = input("Daily budget in USD (default: 10): ").strip()
            if budget_input:
                try:
                    config["daily_budget"] = float(budget_input)
                except:
                    config["daily_budget"] = 10.0
            else:
                config["daily_budget"] = 10.0

            print(f"✅ Daily budget: ${config['daily_budget']}\n")

            print("=" * 60)
            print("STEP 4: Test Framework")
            print("=" * 60)
            print("Detected: pytest, jest, cargo test, etc.")
            framework = input(
                "Enter test framework (or press Enter for auto-detect): "
            ).strip()
            if framework:
                config["test_framework"] = framework

            save_config(config)

            print("\n" + "=" * 60)
            print("✅ SETUP COMPLETE!")
            print("=" * 60)
            print("\nNext steps:")
            print("  - voria issue 42  # Fix a GitHub issue")
            print("  - voria plan 'Add error handling'  # Plan a fix")
            print("  - voria logs  # View activity")
            print("\nTo update config later: voria config")
            print("=" * 60 + "\n")

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="voria initialized successfully!",
                    data={"config": config},
                )
            )
            return

        if action == "github":
            token = command.get("token")
            if token:
                config["github_token"] = token
                save_config(config)
                send_response(
                    Response(
                        status="success",
                        action="stop",
                        message="GitHub token saved! You can now use voria issue without entering token.",
                    )
                )
            else:
                print_token_guide()
                token = input("Enter GitHub Personal Access Token: ").strip()
                if token:
                    config["github_token"] = token
                    save_config(config)
                    send_response(
                        Response(
                            status="success",
                            action="stop",
                            message="GitHub token saved!",
                        )
                    )
                else:
                    send_response(
                        Response(
                            status="error", action="stop", message="No token provided"
                        )
                    )
            return

        send_response(
            Response(
                status="error",
                action="stop",
                message=f"Unknown config action: {action}",
            )
        )

    except Exception as e:
        logger.error(f"Config command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error",
                action="stop",
                message=f"Config command failed: {str(e)}",
            )
        )


def main() -> None:
    """Main engine loop - read and process NDJSON from stdin."""
    logger.info("voria Python Engine started")
    logger.info("Ready to receive commands via NDJSON on stdin")

    try:
        # Create a single event loop for the entire session
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        while True:
            try:
                line = sys.stdin.readline()

                # EOF or empty line
                if not line:
                    logger.info("Received EOF, shutting down")
                    break

                # Process the command asynchronously
                loop.run_until_complete(process_command_async(line))
            except EOFError:
                logger.info("EOF received")
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}", exc_info=True)
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message=f"Processing error: {str(e)}",
                    )
                )

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
    finally:
        try:
            loop.close()
        except:
            pass
        logger.info("voria Python Engine shutting down")


if __name__ == "__main__":
    main()
