"""
Code Patcher Module - Apply and rollback code patches

Supports unified diff format patches, with ability to:
- Parse unified diffs
- Apply patches to files
- Create backups for rollback
- Handle merge conflicts gracefully
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
import shutil

logger = logging.getLogger(__name__)


@dataclass
class PatchHunk:
    """A single hunk from a unified diff"""
    old_file: str
    new_file: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[str]  # Patch lines (with +/- prefix)


class UnifiedDiffParser:
    """Parse unified diff format"""
    
    @staticmethod
    def parse(diff_content: str) -> List[PatchHunk]:
        """
        Parse unified diff format
        
        Example:
        --- a/file.py
        +++ b/file.py
        @@ -10,5 +10,6 @@
         context line
        -old line
        +new line
         context line
        """
        hunks = []
        lines = diff_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for file headers
            if line.startswith('--- '):
                old_file = line[4:].split('\t')[0]
                i += 1
                
                if i < len(lines) and lines[i].startswith('+++ '):
                    new_file = lines[i][4:].split('\t')[0]
                    i += 1
                    
                    # Parse hunks for this file
                    while i < len(lines) and lines[i].startswith('@@'):
                        match = re.match(
                            r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',
                            lines[i]
                        )
                        if match:
                            old_start = int(match.group(1))
                            old_count = int(match.group(2) or 1)
                            new_start = int(match.group(3))
                            new_count = int(match.group(4) or 1)
                            i += 1
                            
                            # Read hunk lines
                            hunk_lines = []
                            while (i < len(lines) and 
                                   not lines[i].startswith('@@') and
                                   not lines[i].startswith('--- ') and
                                   not lines[i].startswith('+++') and
                                   lines[i] and
                                   lines[i][0] in [' ', '-', '+', '\\']):
                                hunk_lines.append(lines[i])
                                i += 1
                            
                            hunks.append(PatchHunk(
                                old_file=old_file.lstrip('a/'),
                                new_file=new_file.lstrip('b/'),
                                old_start=old_start,
                                old_count=old_count,
                                new_start=new_start,
                                new_count=new_count,
                                lines=hunk_lines
                            ))
                        else:
                            i += 1
            else:
                i += 1
        
        return hunks


class CodePatcher:
    """Apply and manage code patches"""
    
    BACKUP_DIR = Path.home() / ".victory" / "backups"
    
    def __init__(self, repo_path: str = "."):
        """Initialize patcher with repo path"""
        self.repo_path = Path(repo_path)
        self.backup_dir = self.BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def apply_patch(
        self,
        patch_content: str,
        strategy: str = "strict"
    ) -> Dict[str, any]:
        """
        Apply a unified diff patch
        
        Args:
            patch_content: Unified diff format patch
            strategy: "strict" (fail on conflict) or "fuzzy" (try best effort)
            
        Returns:
            Dict with status, modified_files, errors
        """
        try:
            logger.info("Parsing patch...")
            hunks = UnifiedDiffParser.parse(patch_content)
            
            if not hunks:
                return {
                    "status": "error",
                    "message": "No valid hunks found in patch",
                    "modified_files": [],
                    "errors": ["Empty patch"]
                }
            
            modified_files = {}
            errors = []
            
            # Group hunks by file
            hunks_by_file = {}
            for hunk in hunks:
                key = hunk.new_file or hunk.old_file
                if key not in hunks_by_file:
                    hunks_by_file[key] = []
                hunks_by_file[key].append(hunk)
            
            # Apply patches to each file
            for file_path, file_hunks in hunks_by_file.items():
                try:
                    result = await self._apply_file_patch(
                        file_path,
                        file_hunks,
                        strategy
                    )
                    modified_files[file_path] = result
                except Exception as e:
                    errors.append(f"{file_path}: {str(e)}")
                    logger.error(f"Failed to patch {file_path}: {e}")
            
            # Check results
            failed_count = sum(1 for r in modified_files.values() if not r["success"])
            
            return {
                "status": "success" if failed_count == 0 else "partial",
                "message": f"Patched {len(modified_files)} files, {failed_count} failed",
                "modified_files": modified_files,
                "errors": errors
            }
        
        except Exception as e:
            logger.error(f"Patch application failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "modified_files": {},
                "errors": [str(e)]
            }
    
    async def _apply_file_patch(
        self,
        file_path: str,
        hunks: List[PatchHunk],
        strategy: str
    ) -> Dict[str, any]:
        """Apply patch hunks to a single file"""
        
        full_path = self.repo_path / file_path
        
        # Check file exists
        if not full_path.exists():
            logger.warning(f"File not found, creating: {file_path}")
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("")
        
        # Create backup
        backup_path = await self._create_backup(full_path)
        
        try:
            # Read current content
            content = full_path.read_text()
            lines = content.split('\n')
            
            # Apply hunks (process in reverse to preserve line numbers)
            for hunk in reversed(sorted(hunks, key=lambda h: h.old_start)):
                lines = await self._apply_hunk(
                    lines,
                    hunk,
                    strategy
                )
            
            # Write patched content
            full_path.write_text('\n'.join(lines))
            
            logger.info(f"Successfully patched: {file_path}")
            
            return {
                "success": True,
                "file": file_path,
                "backup": str(backup_path),
                "hunks_applied": len(hunks)
            }
        
        except Exception as e:
            # Restore backup on failure
            logger.error(f"Patch failed, restoring backup: {e}")
            if backup_path.exists():
                shutil.copy(backup_path, full_path)
            
            return {
                "success": False,
                "file": file_path,
                "error": str(e),
                "backup_restored": True
            }
    
    async def _apply_hunk(
        self,
        lines: List[str],
        hunk: PatchHunk,
        strategy: str
    ) -> List[str]:
        """Apply a single hunk to lines"""
        
        # Parse hunk lines
        context_before = []
        removals = []
        additions = []
        context_after = []
        
        current = None
        
        for line in hunk.lines:
            if line.startswith(' '):
                content = line[1:]
                if not removals and not additions:
                    context_before.append(content)
                else:
                    context_after.append(content)
            elif line.startswith('-'):
                removals.append(line[1:])
                current = 'removal'
            elif line.startswith('+'):
                additions.append(line[1:])
                current = 'addition'
            elif line.startswith('\\'):
                # "\ No newline at end of file"
                pass
        
        # Find hunk location in lines
        start_idx = hunk.old_start - 1
        
        # Try to match context
        if strategy == "strict":
            # Verify exact match
            for i, ctx_line in enumerate(context_before):
                if start_idx + i >= len(lines) or lines[start_idx + i] != ctx_line:
                    raise ValueError(
                        f"Context mismatch at line {hunk.old_start + i}: "
                        f"expected '{ctx_line}', got '{lines[start_idx + i] if start_idx + i < len(lines) else 'EOF'}'"
                    )
        
        # Apply changes
        # Remove old lines
        end_idx = start_idx + hunk.old_count
        new_lines = lines[:start_idx] + additions + lines[end_idx:]
        
        return new_lines
    
    async def _create_backup(self, file_path: Path) -> Path:
        """Create backup of file before patching"""
        
        import time
        timestamp = int(time.time())
        backup_name = f"{file_path.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        
        return backup_path
    
    async def rollback_patch(self, file_path: str, backup_path: str) -> bool:
        """Rollback a patch using backup"""
        
        try:
            full_path = self.repo_path / file_path
            backup = Path(backup_path)
            
            if not backup.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            shutil.copy(backup, full_path)
            logger.info(f"Rolled back: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def cleanup_backups(self, keep_count: int = 10) -> int:
        """Clean up old backups, keeping most recent"""
        
        try:
            if not self.backup_dir.exists():
                return 0
            
            # Get all backups sorted by modification time
            backups = sorted(
                self.backup_dir.glob("*.bak"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remove old ones
            removed = 0
            for backup in backups[keep_count:]:
                backup.unlink()
                removed += 1
            
            logger.info(f"Cleaned {removed} old backups")
            return removed
        
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return 0


async def test_patcher():
    """Test the code patcher"""
    
    # Example patch
    patch = """--- a/example.py
+++ b/example.py
@@ -1,5 +1,6 @@
 def hello():
-    print("old")
+    print("new")
     return True
 
 hello()
"""
    
    patcher = CodePatcher()
    result = await patcher.apply_patch(patch)
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_patcher())
