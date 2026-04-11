"""GitHub API Integration Module

Fetches issues, manages PRs, and handles GitHub workflows.
"""

import logging
import os
from typing import List, Dict, Any, Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


GITHUB_TOKEN_GUIDE = """
================================================================================
                    GITHUB PERSONAL ACCESS TOKEN GUIDE
================================================================================

To access your GitHub issues, you need a Personal Access Token (PAT).

STEP 1: Generate a new token
------------------------
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "victory-cli"
4. Select expiration (recommend: 90 days)

STEP 2: Select scopes (permissions)
---------------------------
✅ repo (Full control of private repositories)
   - This allows reading issues, creating PRs, etc.
   - Required for accessing private repos

STEP 3: Generate token
-------------------
1. Click "Generate token"
2. COPY THE TOKEN IMMEDIATELY - it won't be shown again!

STEP 4: Use the token
-------------------
Save it to environment:
  export GITHUB_TOKEN='ghp_your_token_here'

Or use directly in commands.

SECURITY NOTE: Never commit tokens to git! Add to .gitignore:
  echo 'GITHUB_TOKEN=' >> .gitignore
================================================================================
"""


def print_token_guide() -> None:
    """Print the GitHub token guide to console."""
    print(GITHUB_TOKEN_GUIDE)


def get_github_token(interactive: bool = True) -> Optional[str]:
    """
    Get GitHub token from environment or prompt user.
    
    Args:
        interactive: If True, prompt user for token. If False, only check env.
    
    Returns:
        Token string or None if not available
    """
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        logger.info("Using GitHub token from GITHUB_TOKEN environment")
        return token
    
    if interactive:
        print_token_guide()
        print("\nEnter your GitHub Personal Access Token: ", end="")
        token = input().strip()
        if token:
            return token
    
    return None


@dataclass
class GitHubIssue:
    """GitHub issue representation"""
    id: int
    number: int
    title: str
    body: str
    labels: List[str]
    state: str  # "open" or "closed"
    url: str
    repo: str
    created_at: str
    updated_at: str


class GitHubClient:
    """GitHub API client for fetching issues and managing PRs"""
    
    API_BASE = "https://api.github.com"
    
    def __init__(self, token: str):
        """
        Initialize GitHub client
        
        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=30.0
        )
    
    async def fetch_issue(self, owner: str, repo: str, issue_number: int) -> GitHubIssue:
        """
        Fetch a specific issue
        
        Args:
            owner: Repository owner (username)
            repo: Repository name
            issue_number: Issue number
            
        Returns:
            GitHubIssue object
        """
        url = f"{self.API_BASE}/repos/{owner}/{repo}/issues/{issue_number}"
        
        try:
            logger.debug(f"Fetching issue {owner}/{repo}#{issue_number}")
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            issue = GitHubIssue(
                id=data["id"],
                number=data["number"],
                title=data["title"],
                body=data["body"] or "",
                labels=[label["name"] for label in data.get("labels", [])],
                state=data["state"],
                url=data["html_url"],
                repo=f"{owner}/{repo}",
                created_at=data["created_at"],
                updated_at=data["updated_at"]
            )
            
            logger.info(f"Fetched issue: {issue.title}")
            return issue
        
        except httpx.HTTPError as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    async def fetch_issue_by_url(self, issue_url: str) -> GitHubIssue:
        """
        Fetch issue from GitHub URL
        
        Args:
            issue_url: GitHub issue URL (e.g., https://github.com/owner/repo/issues/123)
            
        Returns:
            GitHubIssue object
        """
        # Parse URL: https://github.com/owner/repo/issues/123
        parts = issue_url.strip("/").split("/")
        owner = parts[-4] if len(parts) >= 4 else None
        repo = parts[-3] if len(parts) >= 3 else None
        number = int(parts[-1]) if len(parts) >= 1 else None
        
        if not all([owner, repo, number]):
            raise ValueError(f"Invalid GitHub URL: {issue_url}")
        
        return await self.fetch_issue(owner, repo, number)
    
    async def create_pr(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a pull request
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            body: PR description
            head: Branch to merge from (e.g., "feature/branch")
            base: Branch to merge into (default: main)
            
        Returns:
            PR data dict
        """
        url = f"{self.API_BASE}/repos/{owner}/{repo}/pulls"
        
        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        try:
            logger.debug(f"Creating PR: {title}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Created PR #{data['number']}: {title}")
            
            return {
                "number": data["number"],
                "url": data["html_url"],
                "id": data["id"],
                "state": data["state"]
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to create PR: {e}")
            raise
    
    async def add_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str
    ) -> Dict[str, Any]:
        """
        Add a comment to an issue or PR
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue/PR number
            body: Comment body
            
        Returns:
            Comment data dict
        """
        url = f"{self.API_BASE}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        
        payload = {"body": body}
        
        try:
            logger.debug(f"Adding comment to {owner}/{repo}#{issue_number}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Added comment to issue #{issue_number}")
            
            return {
                "id": data["id"],
                "url": data["html_url"],
                "body": data["body"]
            }
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to add comment: {e}")
            raise
    
    async def update_issue_status(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        state: str
    ) -> None:
        """
        Update issue status (open/closed)
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            state: "open" or "closed"
        """
        url = f"{self.API_BASE}/repos/{owner}/{repo}/issues/{issue_number}"
        payload = {"state": state}
        
        try:
            logger.debug(f"Updating issue {issue_number} state to {state}")
            response = await self.client.patch(url, json=payload)
            response.raise_for_status()
            logger.info(f"Updated issue #{issue_number} state to {state}")
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to update issue: {e}")
            raise

    async def fetch_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetch all repositories for a user
        
        Args:
            username: GitHub username
            
        Returns:
            List of repository dicts
        """
        url = f"{self.API_BASE}/users/{username}/repos"
        
        try:
            logger.debug(f"Fetching repos for user {username}")
            response = await self.client.get(url, params={"sort": "updated", "per_page": 100})
            response.raise_for_status()
            
            repos = response.json()
            logger.info(f"Found {len(repos)} repos for user {username}")
            return repos
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch repos: {e}")
            raise

    async def fetch_repo_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open"
    ) -> List[GitHubIssue]:
        """
        Fetch all issues for a repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            
        Returns:
            List of GitHubIssue objects
        """
        url = f"{self.API_BASE}/repos/{owner}/{repo}/issues"
        
        try:
            logger.debug(f"Fetching {state} issues for {owner}/{repo}")
            response = await self.client.get(
                url,
                params={"state": state, "per_page": 100, "sort": "created"}
            )
            response.raise_for_status()
            
            issues = []
            for data in response.json():
                if "pull_request" not in data:
                    issue = GitHubIssue(
                        id=data["id"],
                        number=data["number"],
                        title=data["title"],
                        body=data["body"] or "",
                        labels=[label["name"] for label in data.get("labels", [])],
                        state=data["state"],
                        url=data["html_url"],
                        repo=f"{owner}/{repo}",
                        created_at=data["created_at"],
                        updated_at=data["updated_at"]
                    )
                    issues.append(issue)
            
            logger.info(f"Fetched {len(issues)} issues from {owner}/{repo}")
            return issues
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch repo issues: {e}")
            raise

    async def fetch_user_issues(
        self,
        username: str,
        state: str = "open"
    ) -> List[GitHubIssue]:
        """
        Fetch all issues across all repos owned by a user
        
        Args:
            username: GitHub username/owner
            state: Issue state (open, closed, all)
            
        Returns:
            List of GitHubIssue objects from all user repos
        """
        all_issues = []
        
        try:
            repos = await self.fetch_user_repos(username)
            
            for repo in repos[:20]:
                repo_name = repo.get("name")
                try:
                    issues = await self.fetch_repo_issues(username, repo_name, state)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.warning(f"Skipping repo {repo_name}: {e}")
                    continue
            
            logger.info(f"Total issues for user {username}: {len(all_issues)}")
            return all_issues
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch user issues: {e}")
            raise

    async def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get authenticated user info
        
        Returns:
            User dict with login, id, etc.
        """
        url = f"{self.API_BASE}/user"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            user = response.json()
            logger.info(f"Authenticated as: {user.get('login')}")
            return user
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get authenticated user: {e}")
            raise

    async def get_rate_limit(self) -> Dict[str, Any]:
        """
        Get API rate limit status
        
        Returns:
            Rate limit dict with limit, remaining, reset
        """
        url = f"{self.API_BASE}/rate_limit"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get rate limit: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
