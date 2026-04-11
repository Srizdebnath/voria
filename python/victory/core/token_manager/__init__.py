"""Token Manager Module

Tracks LLM token usage across all providers and manages budget limits.

Usage:
    from victory.core.token_manager import get_token_manager

    manager = get_token_manager()
    manager.record_usage("openai", "gpt-4", 500, 1000)
    summary = manager.get_usage_summary()
"""

from .manager import (
    TokenManager,
    TokenBudget,
    TokenUsageRecord,
    get_token_manager,
    init_token_manager,
    PRICING,
)

__all__ = [
    "TokenManager",
    "TokenBudget",
    "TokenUsageRecord",
    "get_token_manager",
    "init_token_manager",
    "PRICING",
]
