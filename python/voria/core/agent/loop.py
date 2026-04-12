"""
Agent Loop - Orchestrates the full voria workflow

Workflow:
1. Plan: Get fix strategy from LLM
2. Patch: Generate code patch from plan
3. Apply: Send patch to Rust for file operations
4. Test: Run test suite
5. Analyze: Check results, decide next action
6. Iterate: Repeat up to max iterations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from voria.core.llm import LLMProviderFactory, Message
from voria.core.executor import TestExecutor, TestSuiteResult
from voria.core.patcher import CodePatcher

logger = logging.getLogger(__name__)


class LoopAction(Enum):
    """Actions the agent loop can take"""

    PLAN = "plan"
    PATCH = "patch"
    APPLY = "apply"
    TEST = "test"
    ANALYZE = "analyze"
    SUCCESS = "success"
    FAILURE = "failure"
    ITERATE = "iterate"


@dataclass
class LoopState:
    """Current state of agent loop"""

    iteration: int = 0
    issue_id: int = 0
    issue_description: str = ""
    repo_path: str = "."

    plan: str = ""
    patch: str = ""
    test_results: Optional[TestSuiteResult] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "iteration": self.iteration,
            "issue_id": self.issue_id,
            "plan": self.plan[:500] if self.plan else "",  # Truncate for logging
            "has_patch": bool(self.patch),
            "test_passed": self.test_results.failed == 0 if self.test_results else None,
            "errors": self.errors[-3:],  # Last 3 errors
        }


class AgentLoop:
    """Main agent loop orchestrator"""

    MAX_ITERATIONS = 5

    def __init__(self, provider_name: str, api_key: str, repo_path: str = "."):
        """
        Initialize agent loop

        Args:
            provider_name: LLM provider (modal, openai, gemini, claude)
            api_key: Provider API key
            repo_path: Path to git repository
        """
        self.provider_name = provider_name
        self.api_key = api_key
        self.repo_path = repo_path

        # Initialize components
        self.provider = None
        self.patcher = CodePatcher(repo_path)
        self.executor = TestExecutor(repo_path)

    async def initialize(self, model: str):
        """Initialize LLM provider with specific model"""
        self.provider = LLMProviderFactory.create(
            provider_name=self.provider_name, api_key=self.api_key, model=model
        )
        logger.info(f"Initialized {self.provider_name} with model {model}")

    async def run(self, issue_id: int, issue_description: str) -> Dict[str, Any]:
        """
        Run full agent loop on issue

        Args:
            issue_id: GitHub issue number
            issue_description: Full issue description/context

        Returns:
            Dict with final status and results
        """

        state = LoopState(
            issue_id=issue_id,
            issue_description=issue_description,
            repo_path=self.repo_path,
        )

        logger.info(f"Starting agent loop for issue #{issue_id}")

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            state.iteration = iteration

            logger.info(f"Iteration {iteration}/{self.MAX_ITERATIONS}")

            try:
                # Step 1: Plan
                action = await self._step_plan(state)
                if action == LoopAction.FAILURE:
                    return self._format_result(state, "failed_plan")

                # Step 2: Generate Patch
                action = await self._step_patch(state)
                if action == LoopAction.FAILURE:
                    return self._format_result(state, "failed_patch")

                # Step 3: Apply Patch (send via NDJSON to Rust)
                action = await self._step_apply(state)
                if action == LoopAction.FAILURE:
                    logger.error("Patch application failed, rolling back...")
                    await self._rollback()
                    # Continue to next iteration
                    continue

                # Step 4: Run Tests
                action = await self._step_test(state)

                # Step 5: Analyze Results
                if action == LoopAction.SUCCESS:
                    logger.info("✅ Issue resolved! Tests passing.")
                    return self._format_result(state, "success")

                elif action == LoopAction.FAILURE:
                    # Analysis step will generate next plan
                    logger.info(
                        f"Tests failed, analyzing for iteration {iteration + 1}..."
                    )
                    await self._analyze_failure(state)

                    if iteration < self.MAX_ITERATIONS:
                        logger.info("Continuing to next iteration...")
                        continue
                    else:
                        logger.warning("Max iterations reached")
                        return self._format_result(state, "max_iterations")

            except Exception as e:
                logger.error(f"Iteration {iteration} failed: {e}")
                state.errors.append(str(e))

        return self._format_result(state, "timeout")

    async def _step_plan(self, state: LoopState) -> LoopAction:
        """Step 1: Generate fix plan"""

        logger.info("Step 1: Planning fix strategy...")

        try:
            if state.iteration == 1:
                # Initial plan from issue
                prompt = state.issue_description
            else:
                # Refined plan based on previous failures
                prompt = f"""{state.issue_description}

Previous attempt failed with:
{state.test_results.stdout if state.test_results else "Unknown"}

Please refine your approach and generate an improved fix."""

            state.plan = await self.provider.plan(prompt)

            logger.info(f"Plan generated ({len(state.plan)} chars)")
            return LoopAction.PLAN

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            state.errors.append(f"Planning: {e}")
            return LoopAction.FAILURE

    async def _step_patch(self, state: LoopState) -> LoopAction:
        """Step 2: Generate code patch"""

        logger.info("Step 2: Generating code patch...")

        try:
            # Get context files (stub - in reality would scan repo)
            context_files = {}

            state.patch = await self.provider.generate_patch(
                issue_description=state.issue_description,
                context_files=context_files,
                previous_errors=None,
            )

            logger.info(f"Patch generated ({len(state.patch)} chars)")
            return LoopAction.PATCH

        except Exception as e:
            logger.error(f"Patch generation failed: {e}")
            state.errors.append(f"Patch generation: {e}")
            return LoopAction.FAILURE

    async def _step_apply(self, state: LoopState) -> LoopAction:
        """Step 3: Apply patch to files"""

        logger.info("Step 3: Applying patch...")

        try:
            result = await self.patcher.apply_patch(state.patch)

            if result["status"] == "success" or result["status"] == "partial":
                logger.info(f"Patch applied: {result['message']}")
                return LoopAction.APPLY
            else:
                logger.error(f"Patch application failed: {result['message']}")
                state.errors.append(result["message"])
                return LoopAction.FAILURE

        except Exception as e:
            logger.error(f"Patch application error: {e}")
            state.errors.append(f"Patch application: {e}")
            return LoopAction.FAILURE

    async def _step_test(self, state: LoopState) -> LoopAction:
        """Step 4: Run tests"""

        logger.info("Step 4: Running tests...")

        try:
            state.test_results = await self.executor.run_tests()

            logger.info(
                f"Tests complete: {state.test_results.passed}/{state.test_results.total} passed"
            )

            if state.test_results.failed == 0:
                return LoopAction.SUCCESS
            else:
                return LoopAction.FAILURE

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            state.errors.append(f"Test execution: {e}")
            return LoopAction.FAILURE

    async def _analyze_failure(self, state: LoopState):
        """Analyze test failure and suggest improvements"""

        logger.info("Analyzing test failure...")

        try:
            if state.test_results:
                analysis = await self.provider.analyze_test_failure(
                    test_output=state.test_results.stdout, code_context=state.patch
                )

                logger.info(
                    f"Analysis complete: {analysis.get('suggestions', '')[:200]}"
                )

                # Update issue description for next iteration
                state.issue_description = f"""{state.issue_description}

Failed attempt #{state.iteration}:
{analysis.get('issue', 'Unknown issue')}

Suggested fix:
{analysis.get('suggestions', 'Try different approach')}"""

        except Exception as e:
            logger.error(f"Failure analysis failed: {e}")
            state.errors.append(f"Failure analysis: {e}")

    async def _rollback(self):
        """Rollback applied patches"""

        logger.info("Rolling back applied patches...")
        # Patcher will automatically restore backups

    def _format_result(self, state: LoopState, status: str) -> Dict[str, Any]:
        """Format final result"""

        return {
            "status": status,
            "issue_id": state.issue_id,
            "iterations": state.iteration,
            "plan": state.plan[:200] if state.plan else None,
            "test_results": (
                {
                    "total": state.test_results.total if state.test_results else 0,
                    "passed": state.test_results.passed if state.test_results else 0,
                    "failed": state.test_results.failed if state.test_results else 0,
                }
                if state.test_results
                else None
            ),
            "errors": state.errors,
            "final_state": state.to_dict(),
        }


async def demo_agent_loop():
    """Demo agent loop"""

    # Example: use Modal free token
    loop = AgentLoop(
        provider_name="modal",
        api_key="your-modal-token",  # Would come from env var
        repo_path=".",
    )

    # Initialize with GLM-5.1-FP8
    await loop.initialize("zai-org/GLM-5.1-FP8")

    # Run on an issue
    result = await loop.run(
        issue_id=123, issue_description="Fix Unicode parsing in parser.py"
    )

    print(f"Final Status: {result['status']}")
    print(f"Iterations: {result['iterations']}")
    print(
        f"Tests Passed: {result['test_results']['passed']}/{result['test_results']['total']}"
    )


if __name__ == "__main__":
    asyncio.run(demo_agent_loop())
