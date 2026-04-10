"""Token Usage Management Module

Tracks LLM token usage and costs across all providers.
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


# Provider pricing (per 1M tokens)
PRICING = {
    "modal": {
        "zai-org/GLM-5.1-FP8": {
            "input": 0.0,  # Free until April 30th
            "output": 0.0
        }
    },
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    },
    "gemini": {
        "gemini-pro": {"input": 0.0005, "output": 0.0015},
    },
    "claude": {
        "claude-3-opus-20240229": {
            "input": 0.015,
            "output": 0.075
        },
        "claude-3-sonnet-20240229": {
            "input": 0.003,
            "output": 0.015
        },
        "claude-3-haiku-20240307": {
            "input": 0.00025,
            "output": 0.00125
        }
    }
}


@dataclass
class TokenUsageRecord:
    """Record of a single token usage event"""
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cost: float = 0.0


@dataclass
class TokenBudget:
    """Token budget configuration"""
    max_tokens: int = 100000  # Total token budget
    warning_threshold: float = 0.7  # Warn at 70% usage
    stop_threshold: float = 0.9  # Stop at 90% usage
    max_cost: float = 100.0  # Stop at $100


class TokenManager:
    """Manages token usage and budget tracking"""
    
    def __init__(self, budget: TokenBudget = None):
        """
        Initialize token manager
        
        Args:
            budget: Token budget configuration
        """
        self.budget = budget or TokenBudget()
        self.records: list[TokenUsageRecord] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> TokenUsageRecord:
        """
        Record token usage from an LLM call
        
        Args:
            provider: LLM provider name
            model: Model identifier
            input_tokens: Input token count
            output_tokens: Output token count
            
        Returns:
            TokenUsageRecord
        """
        total_tokens = input_tokens + output_tokens
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
        
        record = TokenUsageRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost
        )
        
        self.records.append(record)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        
        logger.info(
            f"Recorded: {total_tokens} tokens ({provider}/{model}), "
            f"Cost: ${cost:.4f}, Total cost: ${self.total_cost:.2f}"
        )
        
        self._check_limits()
        
        return record
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for token usage"""
        try:
            pricing = PRICING.get(provider, {}).get(model)
            if not pricing:
                logger.warning(f"No pricing data for {provider}/{model}")
                return 0.0
            
            input_cost = (input_tokens / 1_000_000) * pricing.get("input", 0)
            output_cost = (output_tokens / 1_000_000) * pricing.get("output", 0)
            
            return input_cost + output_cost
        
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.0
    
    def _check_limits(self) -> None:
        """Check if token usage exceeds limits"""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        usage_percent = total_tokens / self.budget.max_tokens
        
        if usage_percent >= self.budget.stop_threshold:
            logger.warning(
                f"Token usage at {usage_percent*100:.1f}% threshold "
                f"({total_tokens}/{self.budget.max_tokens})"
            )
        
        if self.total_cost >= self.budget.max_cost:
            logger.warning(
                f"Cost limit reached: ${self.total_cost:.2f} "
                f"(budget: ${self.budget.max_cost})"
            )
    
    def get_remaining_tokens(self) -> int:
        """Get remaining tokens in budget"""
        total = self.total_input_tokens + self.total_output_tokens
        return max(0, self.budget.max_tokens - total)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary statistics"""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        usage_percent = (total_tokens / self.budget.max_tokens) * 100
        
        # Group by provider
        by_provider = {}
        for record in self.records:
            if record.provider not in by_provider:
                by_provider[record.provider] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
            by_provider[record.provider]["calls"] += 1
            by_provider[record.provider]["tokens"] += record.total_tokens
            by_provider[record.provider]["cost"] += record.cost
        
        return {
            "total_tokens": total_tokens,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "remaining_tokens": self.get_remaining_tokens(),
            "usage_percent": usage_percent,
            "total_cost": self.total_cost,
            "budget": {
                "max_tokens": self.budget.max_tokens,
                "max_cost": self.budget.max_cost,
                "warning_threshold": self.budget.warning_threshold,
                "stop_threshold": self.budget.stop_threshold
            },
            "by_provider": by_provider,
            "num_calls": len(self.records)
        }
    
    def should_stop(self) -> bool:
        """Check if processing should stop due to limits"""
        total = self.total_input_tokens + self.total_output_tokens
        
        if total >= self.budget.max_tokens * self.budget.stop_threshold:
            return True
        
        if self.total_cost >= self.budget.max_cost:
            return True
        
        return False
    
    def log_summary(self) -> None:
        """Log usage summary"""
        summary = self.get_usage_summary()
        
        logger.info("=" * 60)
        logger.info("Token Usage Summary")
        logger.info("=" * 60)
        logger.info(f"Total tokens: {summary['total_tokens']:,}")
        logger.info(f"  Input: {summary['input_tokens']:,}")
        logger.info(f"  Output: {summary['output_tokens']:,}")
        logger.info(f"  Remaining: {summary['remaining_tokens']:,}")
        logger.info(f"Usage: {summary['usage_percent']:.1f}% of budget")
        logger.info(f"Total cost: ${summary['total_cost']:.2f}")
        
        if summary["by_provider"]:
            logger.info("\nBy Provider:")
            for provider, stats in summary["by_provider"].items():
                logger.info(
                    f"  {provider}: "
                    f"{stats['calls']} calls, "
                    f"{stats['tokens']:,} tokens, "
                    f"${stats['cost']:.2f}"
                )
        
        logger.info("=" * 60)


# Global token manager instance
_token_manager: TokenManager = None


def get_token_manager() -> TokenManager:
    """Get or create global token manager"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager


def init_token_manager(budget: TokenBudget) -> TokenManager:
    """Initialize global token manager with custom budget"""
    global _token_manager
    _token_manager = TokenManager(budget)
    return _token_manager
