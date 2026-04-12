"""GitHub Integration Module

Provides GitHub API access for fetching issues and managing pull requests.

Usage:
    from voria.core.github import GitHubClient, print_token_guide

    # Guide user on how to get GitHub token
    print_token_guide()

    # Or get token interactively
    from voria.core.github import get_github_token
    token = get_github_token()

    client = GitHubClient(token="ghp_...")
    issue = await client.fetch_issue("owner", "repo", 123)
"""

from .client import (
    GitHubClient,
    GitHubIssue,
    print_token_guide,
    get_github_token,
    GITHUB_TOKEN_GUIDE,
)

__all__ = [
    "GitHubClient",
    "GitHubIssue",
    "print_token_guide",
    "get_github_token",
    "GITHUB_TOKEN_GUIDE",
]
