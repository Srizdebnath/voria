"""Code Patcher Module - Apply unified diff patches"""

from .patcher import CodePatcher, UnifiedDiffParser, PatchHunk

__all__ = [
    "CodePatcher",
    "UnifiedDiffParser",
    "PatchHunk",
]
