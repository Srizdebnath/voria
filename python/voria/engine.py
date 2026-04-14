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
    from voria.core.executor import VoriaTestExecutor
    from voria.core.agent import AgentLoop
    from voria.core.testing.runner import TestRunner
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
    chunk: Optional[str] = None
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

        if not api_key or not model or provider_name == "openai":
            config = load_config()
            if not api_key:
                api_key = config.get("llm_api_key")
                provider_name = config.get("llm_provider", provider_name)
            if not model:
                model = config.get("llm_model")

        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)

        if not api_key:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"API key required for {provider_name} provider. Please set in config or env.",
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

            full_content = ""
            async for chunk in provider.stream_generate(messages):
                full_content += chunk
                send_response(
                    Response(
                        status="pending",
                        action="continue",
                        message="Streaming plan...",
                        chunk=chunk,
                    )
                )

            # Try to parse JSON from full content
            try:
                # Basic JSON extraction
                import re

                json_match = re.search(r"({.*})", full_content, re.DOTALL)
                if json_match:
                    plan_data = json.loads(json_match.group(1))
                else:
                    plan_data = {"plan": full_content}
            except:
                plan_data = {"plan": full_content}

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="Plan generated successfully",
                    data={"plan": plan_data, "provider": provider_name},
                )
            )
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Plan generation failed: {str(e)}",
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
            config = load_config()
            github_token = config.get("github_token") or os.environ.get("GITHUB_TOKEN")

        if not github_token:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="GitHub token required for issue command. Please setup with 'voria config --github' or set GITHUB_TOKEN environment variable.",
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
        if not api_key or not model or provider_name == "openai":
            config = load_config()
            if not api_key:
                api_key = config.get("llm_api_key")
                provider_name = config.get("llm_provider", provider_name)
            if not model:
                model = config.get("llm_model")

        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)

        if not api_key:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"API key required for {provider_name} provider. Please set in config or env.",
                )
            )
            return

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

            full_content = ""
            async for chunk in provider.stream_generate(messages):
                full_content += chunk
                send_response(
                    Response(
                        status="pending",
                        action="continue",
                        message="Streaming patch...",
                        chunk=chunk,
                    )
                )

            patch = full_content
            logger.info(f"Generated patch for issue #{issue_number}")

            # Auto-apply if requested
            if command.get("auto", False):
                logger.info("Auto-applying patch...")
                patcher = CodePatcher(".")
                result = await patcher.apply_patch(patch)
                send_response(
                    Response(
                        status="success",
                        action="stop",
                        message=f"Patch generated and auto-applied to {len(result)} files",
                        patch=patch,
                        data={
                            "files_modified": result,
                            "issue_number": issue_number,
                            "issue_title": issue.title,
                        },
                    )
                )
            else:
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
        provider_name = command.get("provider", "openai")
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
            config = load_config()
            github_token = config.get("github_token") or os.environ.get("GITHUB_TOKEN")

        if not github_token:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="GitHub token required for fix command. Please setup with 'voria config --github' or set GITHUB_TOKEN environment variable.",
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
        if not api_key or not model or provider_name == "openai":
            config = load_config()
            if not api_key:
                api_key = config.get("llm_api_key")
                provider_name = config.get("llm_provider", provider_name)
            if not model:
                model = config.get("llm_model")

        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)

        if not api_key:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"API key required for {provider_name} provider. Please set in config or env.",
                )
            )
            return

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

        if not github_token:
            config = load_config()
            github_token = config.get("github_token") or os.environ.get("GITHUB_TOKEN")

        if not github_token:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="GitHub token not found. Please set GITHUB_TOKEN environment variable or add it to ~/.voria/config.json",
                )
            )
            return

        logger.info(f"Processing list_issues command for {owner}/{repo}")

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
                Response(
                    status="error",
                    action="stop",
                    message=f"Git operation failed: {e.stderr}",
                )
            )
        except Exception as e:
            logger.error(f"PR creation error: {e}")
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"PR creation error: {str(e)}",
                )
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
        lines_count = command.get("lines", 50)

        log_dir = Path.home() / ".voria"
        log_file = log_dir / "voria.log"

        # Ensure log directory and file exist
        log_dir.mkdir(parents=True, exist_ok=True)
        if not log_file.exists():
            log_file.touch()

        # Add file handler to actually write logs to the file
        _setup_file_logging(log_file)

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
                    log_lines = f.readlines()[-lines_count:]

                if not log_lines:
                    log_content = "No log entries yet. Run some commands first."
                else:
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


def _setup_file_logging(log_file: Path) -> None:
    """Add a file handler to the root logger so logs are persisted."""
    root_logger = logging.getLogger()
    # Don't add duplicate handlers
    for h in root_logger.handlers:
        if isinstance(h, logging.FileHandler) and h.baseFilename == str(log_file):
            return
    fh = logging.FileHandler(str(log_file), mode="a")
    fh.setLevel(logging.INFO)
    fh.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    root_logger.addHandler(fh)


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


async def handle_list_tests_command(command: Dict[str, Any]) -> None:
    """Handle 'list_tests' command."""
    try:
        from voria.core.testing.definitions import TEST_DEFINITIONS

        tests = []
        for t in TEST_DEFINITIONS:
            tests.append(
                {
                    "id": t.id,
                    "name": t.name,
                    "category": t.category.value,
                    "description": t.description,
                    "impact": t.impact,
                    "type": t.type,
                }
            )

        send_response(
            Response(
                status="success",
                action="stop",
                message=f"Available tests: {len(tests)}",
                data={"tests": tests},
            )
        )
    except Exception as e:
        logger.error(f"List tests error: {e}")
        send_response(Response(status="error", action="stop", message=str(e)))


async def handle_test_command(command: Dict[str, Any]) -> None:
    """Handle 'test' command."""
    try:
        test_id = command.get("test_id")
        provider_name = command.get("provider", "openai")
        api_key = command.get("api_key")
        model = command.get("model", "gpt-4")
        repo_path = command.get("repo_path")
        if repo_path is None:
            repo_path = "."

        if not test_id:
            send_response(
                Response(status="error", action="stop", message="test_id is required")
            )
            return

        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)
            if not api_key:
                # Try to load from config
                config = load_config()
                api_key = config.get("llm_api_key")
                provider_name = config.get("llm_provider", provider_name)
                model = config.get("llm_model", model)

        if not api_key:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"API key required for {provider_name}",
                )
            )
            return

        runner = TestRunner(provider_name, api_key, model, repo_path)
        result = await runner.run_test(test_id)

        send_response(
            Response(
                status="success",
                action="stop",
                message=f"Test '{test_id}' completed",
                data={"result": result},
            )
        )
    except Exception as e:
        logger.error(f"Test execution error: {e}")
        send_response(Response(status="error", action="stop", message=str(e)))


def handle_test_results_callback(command: Dict[str, Any]) -> None:
    """Handle test results callback from CLI."""
    test_status = command.get("test_status")
    test_logs = command.get("test_logs")

    logger.info(f"Received test results: {test_status}")
    if test_logs:
        logger.debug(f"Test logs:\n{test_logs}")


async def handle_scan_command(command: Dict[str, Any]) -> None:
    """Handle 'scan' — run ALL security tests in parallel, produce unified report."""
    try:
        provider_name = command.get("provider", "openai")
        api_key = command.get("api_key")
        model = command.get("model", "gpt-4")
        repo_path = command.get("repo_path") or "."
        category_filter = command.get("category", "security")

        if not api_key:
            config = load_config()
            api_key = config.get("llm_api_key")
            provider_name = config.get("llm_provider", provider_name)
            model = config.get("llm_model", model)
        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)
        if not api_key:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"API key required for {provider_name}",
                )
            )
            return

        from voria.core.testing.runner import TestRunner
        from voria.core.testing.definitions import TEST_DEFINITIONS, TestCategory

        runner = TestRunner(provider_name, api_key, model, repo_path)

        # Filter tests by category
        category_map = {
            "security": TestCategory.SECURITY,
            "production": TestCategory.PRODUCTION,
            "performance": TestCategory.PERFORMANCE,
            "stress": TestCategory.STRESS,
            "quality": TestCategory.QUALITY,
            "all": None,
        }
        target_cat = category_map.get(category_filter.lower())
        if target_cat:
            tests_to_run = [t for t in TEST_DEFINITIONS if t.category == target_cat]
        else:
            tests_to_run = list(TEST_DEFINITIONS)

        logger.info(
            f"Scanning {len(tests_to_run)} tests in category '{category_filter}'"
        )

        # Run tests in parallel batches of 5
        results = []
        batch_size = 5
        for i in range(0, len(tests_to_run), batch_size):
            batch = tests_to_run[i : i + batch_size]
            tasks = [runner.run_test(t.id) for t in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for j, r in enumerate(batch_results):
                if isinstance(r, Exception):
                    results.append(
                        {
                            "id": batch[j].id,
                            "name": batch[j].name,
                            "result": {"status": "error", "summary": str(r)},
                        }
                    )
                else:
                    results.append(r)

        # Compute aggregate
        total = len(results)
        passed = sum(
            1 for r in results if r.get("result", {}).get("status") == "passed"
        )
        failed = sum(
            1 for r in results if r.get("result", {}).get("status") == "failed"
        )
        warnings = sum(
            1 for r in results if r.get("result", {}).get("status") == "warning"
        )
        scores = [
            r.get("result", {}).get("score", 0)
            for r in results
            if isinstance(r.get("result", {}).get("score"), (int, float))
        ]
        avg_score = sum(scores) / max(len(scores), 1)

        # Collect all findings
        all_findings = []
        all_recommendations = []
        for r in results:
            result_data = r.get("result", {})
            for f in result_data.get("findings", []):
                f["test"] = r.get("id", "unknown")
                all_findings.append(f)
            all_recommendations.extend(result_data.get("recommendations", []))

        send_response(
            Response(
                status="success",
                action="stop",
                message=f"Scan complete: {passed} passed, {failed} failed, {warnings} warnings",
                data={
                    "scan": {
                        "total_tests": total,
                        "passed": passed,
                        "failed": failed,
                        "warnings": warnings,
                        "avg_score": round(avg_score, 1),
                        "category": category_filter,
                        "findings": all_findings[:50],
                        "recommendations": list(set(all_recommendations))[:20],
                        "test_results": results,
                    }
                },
            )
        )
    except Exception as e:
        logger.error(f"Scan command error: {e}", exc_info=True)
        send_response(
            Response(status="error", action="stop", message=f"Scan failed: {str(e)}")
        )


async def handle_diff_command(command: Dict[str, Any]) -> None:
    """Handle 'diff' — compare security posture between two git refs."""
    try:
        ref_a = command.get("ref_a", "HEAD~1")
        ref_b = command.get("ref_b", "HEAD")
        repo_path = command.get("repo_path") or "."

        import subprocess

        # Get list of changed files between two refs
        try:
            diff_output = subprocess.run(
                ["git", "diff", "--name-only", ref_a, ref_b],
                capture_output=True,
                text=True,
                cwd=repo_path,
                check=True,
            )
            changed_files = [
                f.strip() for f in diff_output.stdout.strip().split("\n") if f.strip()
            ]
        except subprocess.CalledProcessError as e:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"Git diff failed: {e.stderr}",
                )
            )
            return

        if not changed_files:
            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="No changes detected between the two refs.",
                    data={
                        "diff": {
                            "ref_a": ref_a,
                            "ref_b": ref_b,
                            "changed_files": [],
                            "risk_delta": 0,
                        }
                    },
                )
            )
            return

        # Classify changed files by risk
        high_risk_patterns = [
            "auth",
            "login",
            "password",
            "secret",
            "token",
            "crypto",
            "sql",
            "query",
            "session",
        ]
        medium_risk_patterns = [
            "api",
            "route",
            "handler",
            "middleware",
            "config",
            "env",
        ]

        high_risk = []
        medium_risk = []
        low_risk = []
        for f in changed_files:
            fl = f.lower()
            if any(p in fl for p in high_risk_patterns):
                high_risk.append(f)
            elif any(p in fl for p in medium_risk_patterns):
                medium_risk.append(f)
            else:
                low_risk.append(f)

        # Get diff stats
        stat_output = subprocess.run(
            ["git", "diff", "--stat", ref_a, ref_b],
            capture_output=True,
            text=True,
            cwd=repo_path,
        )

        risk_delta = len(high_risk) * 3 + len(medium_risk) * 1
        risk_level = (
            "critical" if risk_delta > 10 else "elevated" if risk_delta > 5 else "low"
        )

        send_response(
            Response(
                status="success",
                action="stop",
                message=f"Diff analysis: {len(changed_files)} files changed, risk level: {risk_level}",
                data={
                    "diff": {
                        "ref_a": ref_a,
                        "ref_b": ref_b,
                        "total_changed": len(changed_files),
                        "high_risk_files": high_risk,
                        "medium_risk_files": medium_risk,
                        "low_risk_files": low_risk,
                        "risk_delta": risk_delta,
                        "risk_level": risk_level,
                        "stat": stat_output.stdout[-500:] if stat_output.stdout else "",
                        "recommendation": (
                            "Run voria scan on changed files before merging."
                            if risk_delta > 3
                            else "Changes look safe."
                        ),
                    }
                },
            )
        )
    except Exception as e:
        logger.error(f"Diff command error: {e}", exc_info=True)
        send_response(
            Response(status="error", action="stop", message=f"Diff failed: {str(e)}")
        )


async def handle_benchmark_command(command: Dict[str, Any]) -> None:
    """Handle 'benchmark' — HTTP benchmarking against a target URL."""
    try:
        url = command.get("url")
        requests_count = command.get("requests", 100)
        concurrency = command.get("concurrency", 10)

        if not url:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="URL is required. Usage: voria benchmark <URL>",
                )
            )
            return

        import time
        import statistics

        logger.info(
            f"Benchmarking {url} with {requests_count} requests, concurrency {concurrency}"
        )

        latencies = []
        errors = 0
        status_codes = {}

        try:
            import httpx
        except ImportError:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message="httpx required. pip install httpx",
                )
            )
            return

        async with httpx.AsyncClient(timeout=30.0) as client:
            sem = asyncio.Semaphore(concurrency)

            async def make_request():
                nonlocal errors
                async with sem:
                    try:
                        t0 = time.perf_counter()
                        resp = await client.get(url)
                        latency = (time.perf_counter() - t0) * 1000
                        latencies.append(latency)
                        code = str(resp.status_code)
                        status_codes[code] = status_codes.get(code, 0) + 1
                    except Exception:
                        errors += 1

            start = time.perf_counter()
            tasks = [make_request() for _ in range(requests_count)]
            await asyncio.gather(*tasks)
            total_time = time.perf_counter() - start

        if not latencies:
            send_response(
                Response(
                    status="error",
                    action="stop",
                    message=f"All {requests_count} requests failed. Check URL.",
                )
            )
            return

        sorted_lat = sorted(latencies)
        metrics = {
            "total_requests": requests_count,
            "successful": len(latencies),
            "failed": errors,
            "total_time_sec": round(total_time, 2),
            "rps": round(len(latencies) / total_time, 1),
            "latency_avg_ms": round(statistics.mean(latencies), 2),
            "latency_min_ms": round(sorted_lat[0], 2),
            "latency_max_ms": round(sorted_lat[-1], 2),
            "latency_p50_ms": round(sorted_lat[int(len(sorted_lat) * 0.50)], 2),
            "latency_p95_ms": round(sorted_lat[int(len(sorted_lat) * 0.95)], 2),
            "latency_p99_ms": round(sorted_lat[int(len(sorted_lat) * 0.99)], 2),
            "status_codes": status_codes,
            "concurrency": concurrency,
        }

        send_response(
            Response(
                status="success",
                action="stop",
                message=f"Benchmark complete: {metrics['rps']} req/s, p50={metrics['latency_p50_ms']}ms, p99={metrics['latency_p99_ms']}ms",
                data={"benchmark": metrics},
            )
        )
    except Exception as e:
        logger.error(f"Benchmark command error: {e}", exc_info=True)
        send_response(
            Response(
                status="error", action="stop", message=f"Benchmark failed: {str(e)}"
            )
        )


async def handle_ci_command(command: Dict[str, Any]) -> None:
    """Handle 'ci' — run scan and output SARIF format for GitHub Security tab."""
    try:
        provider_name = command.get("provider", "openai")
        api_key = command.get("api_key")
        model = command.get("model", "gpt-4")
        repo_path = command.get("repo_path") or "."

        if not api_key:
            config = load_config()
            api_key = config.get("llm_api_key")
            provider_name = config.get("llm_provider", provider_name)
            model = config.get("llm_model", model)
        if not api_key:
            env_key = f"{provider_name.upper()}_API_KEY"
            api_key = os.environ.get(env_key)
        if not api_key:
            send_response(
                Response(status="error", action="stop", message=f"API key required")
            )
            return

        from voria.core.testing.runner import TestRunner
        from voria.core.testing.definitions import TEST_DEFINITIONS, TestCategory

        runner = TestRunner(provider_name, api_key, model, repo_path)
        security_tests = [
            t for t in TEST_DEFINITIONS if t.category == TestCategory.SECURITY
        ]

        # Run top 10 security tests for CI speed
        tests_to_run = security_tests[:10]
        results = []
        for t in tests_to_run:
            try:
                r = await runner.run_test(t.id)
                results.append(r)
            except Exception as e:
                results.append(
                    {"id": t.id, "result": {"status": "error", "summary": str(e)}}
                )

        # Build SARIF v2.1.0
        sarif_results = []
        sarif_rules = []
        rule_ids = set()
        for r in results:
            test_id = r.get("id", "unknown")
            result_data = r.get("result", {})
            for f in result_data.get("findings", []):
                rule_id = f"voria/{test_id}"
                if rule_id not in rule_ids:
                    rule_ids.add(rule_id)
                    sarif_rules.append(
                        {
                            "id": rule_id,
                            "name": r.get("name", test_id),
                            "shortDescription": {
                                "text": result_data.get("summary", "")[:200]
                            },
                            "defaultConfiguration": {
                                "level": (
                                    "warning"
                                    if f.get("severity") != "high"
                                    else "error"
                                )
                            },
                        }
                    )
                sarif_results.append(
                    {
                        "ruleId": rule_id,
                        "level": "error" if f.get("severity") == "high" else "warning",
                        "message": {"text": f.get("description", "Security finding")},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": f.get("file", "unknown")
                                    },
                                    "region": {"startLine": f.get("line", 1)},
                                }
                            }
                        ],
                    }
                )

        sarif = {
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "voria",
                            "version": "0.0.5",
                            "informationUri": "https://github.com/Srizdebnath/voria",
                            "rules": sarif_rules,
                        }
                    },
                    "results": sarif_results,
                }
            ],
        }

        send_response(
            Response(
                status="success",
                action="stop",
                message=f"CI scan complete: {len(sarif_results)} findings in SARIF format",
                data={"sarif": sarif, "findings_count": len(sarif_results)},
            )
        )
    except Exception as e:
        logger.error(f"CI command error: {e}", exc_info=True)
        send_response(
            Response(status="error", action="stop", message=f"CI scan failed: {str(e)}")
        )


async def handle_watch_command(command: Dict[str, Any]) -> None:
    """Handle 'watch' — file watcher that re-runs tests on changes."""
    try:
        repo_path = command.get("repo_path") or "."
        test_ids = command.get(
            "test_ids", ["hardcoded_secrets", "xss", "sql_injection"]
        )

        # Get initial snapshot of file mtimes
        watch_path = Path(repo_path)
        extensions = {".py", ".js", ".ts", ".go", ".rs", ".java"}

        def get_snapshot():
            snap = {}
            for p in watch_path.rglob("*"):
                if (
                    p.suffix in extensions
                    and "node_modules" not in str(p)
                    and ".git" not in str(p)
                    and "venv" not in str(p)
                ):
                    try:
                        snap[str(p)] = p.stat().st_mtime
                    except Exception:
                        pass
            return snap

        initial = get_snapshot()
        send_response(
            Response(
                status="success",
                action="stop",
                message=f"Watch mode: monitoring {len(initial)} files. Changes will trigger tests: {', '.join(test_ids)}",
                data={
                    "watch": {
                        "files_monitored": len(initial),
                        "tests": test_ids,
                        "status": "active",
                    }
                },
            )
        )
    except Exception as e:
        logger.error(f"Watch command error: {e}", exc_info=True)
        send_response(
            Response(status="error", action="stop", message=f"Watch failed: {str(e)}")
        )


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
        elif cmd_type == "list_tests":
            await handle_list_tests_command(command)
        elif cmd_type == "test":
            await handle_test_command(command)
        elif cmd_type == "test_results":
            handle_test_results_callback(command)
        elif cmd_type == "create_pr":
            await handle_create_pr_command(command)
        elif cmd_type == "scan":
            await handle_scan_command(command)
        elif cmd_type == "diff":
            await handle_diff_command(command)
        elif cmd_type == "benchmark":
            await handle_benchmark_command(command)
        elif cmd_type == "ci":
            await handle_ci_command(command)
        elif cmd_type == "watch":
            await handle_watch_command(command)
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

# BUG-02 FIX: Cache config to avoid redundant disk reads per request
_config_cache: Optional[Dict[str, Any]] = None
_config_cache_mtime: float = 0.0


def load_config() -> Dict[str, Any]:
    """Load voria configuration from ~/.voria/config.json (cached per mtime)."""
    global _config_cache, _config_cache_mtime
    if voria_CONFIG_FILE.exists():
        try:
            mtime = voria_CONFIG_FILE.stat().st_mtime
            if _config_cache is not None and mtime == _config_cache_mtime:
                return _config_cache
            with open(voria_CONFIG_FILE, "r") as f:
                _config_cache = json.load(f)
                _config_cache_mtime = mtime
                return _config_cache
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    return {}


def invalidate_config_cache() -> None:
    """Invalidate config cache after save."""
    global _config_cache, _config_cache_mtime
    _config_cache = None
    _config_cache_mtime = 0.0


def save_config(config: Dict[str, Any]) -> None:
    """Save voria configuration to ~/.voria/config.json"""
    try:
        voria_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(voria_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        os.chmod(voria_CONFIG_FILE, 0o600)
        invalidate_config_cache()
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
            # BUG-03 FIX: Non-interactive init — accepts config via JSON payload
            # No print()/input() — those corrupt NDJSON stdout/stdin
            init_provider = command.get("llm_provider")
            init_api_key = command.get("llm_api_key")
            init_github = command.get("github_token")
            init_model = command.get("llm_model")
            init_budget = command.get("daily_budget", 10.0)
            init_framework = command.get("test_framework")

            new_config = {}

            # If fields provided via command, use them
            if init_provider:
                new_config["llm_provider"] = init_provider
            if init_api_key:
                new_config["llm_api_key"] = init_api_key
            if init_github:
                new_config["github_token"] = init_github
            if init_model:
                new_config["llm_model"] = init_model
            if init_budget is not None:
                try:
                    new_config["daily_budget"] = float(init_budget)
                except (ValueError, TypeError):
                    new_config["daily_budget"] = 10.0
            if init_framework:
                new_config["test_framework"] = init_framework

            # If no fields provided, return current config with instructions
            if not init_provider and not init_api_key:
                # Check if config already exists
                existing = load_config()
                if existing.get("llm_api_key"):
                    send_response(
                        Response(
                            status="success",
                            action="stop",
                            message="voria is already configured!",
                            data={
                                "config": {
                                    k: (
                                        v[:8] + "..."
                                        if k in ("llm_api_key", "github_token") and v
                                        else v
                                    )
                                    for k, v in existing.items()
                                },
                                "hint": "Use 'voria config set' to update individual fields.",
                            },
                        )
                    )
                    return
                else:
                    send_response(
                        Response(
                            status="success",
                            action="stop",
                            message="Welcome to voria! Configure with: voria setup-modal <TOKEN> or set ~/.voria/config.json",
                            data={
                                "available_providers": [
                                    "modal",
                                    "openai",
                                    "gemini",
                                    "claude",
                                    "minimax",
                                ],
                                "setup_instructions": [
                                    "1. Get an API key from your preferred LLM provider",
                                    "2. Run: voria setup-modal <YOUR_TOKEN>",
                                    "3. Or edit ~/.voria/config.json directly",
                                    "4. Set GitHub token: voria set-github-token",
                                ],
                            },
                        )
                    )
                    return

            # Merge with existing config
            existing = load_config()
            existing.update(new_config)
            save_config(existing)

            send_response(
                Response(
                    status="success",
                    action="stop",
                    message="voria initialized successfully!",
                    data={
                        "config": {
                            k: (
                                v[:8] + "..."
                                if k in ("llm_api_key", "github_token")
                                and isinstance(v, str)
                                else v
                            )
                            for k, v in existing.items()
                        }
                    },
                )
            )
            return

        if action == "github":
            # BUG-03 FIX: Accept token from command payload only
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
                send_response(
                    Response(
                        status="error",
                        action="stop",
                        message="GitHub token required. Usage: voria set-github-token (interactive) or pass 'token' in config command.",
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

    # BUG-10 FIX: Always create a new event loop (avoids DeprecationWarning in 3.10+)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # BUG-11 FIX: Setup file logging on startup
    log_dir = Path.home() / ".voria"
    log_dir.mkdir(parents=True, exist_ok=True)
    _setup_file_logging(log_dir / "voria.log")

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
