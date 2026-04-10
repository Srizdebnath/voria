# Plugin Development Guide

How to create and integrate plugins for Victory.

##  What Are Plugins?

Plugins extend Victory to support additional:
- **Programming languages** (test frameworks, code parsers)
- **VCS systems** (GitHub, GitLab, Gitea)
- **CI/CD platforms** (Jenkins, CircleCI, GitHub Actions)
- **LLM providers** (via the core llm module)

##  Plugin Types

### 1. Language Plugins

Add support for new programming languages.

**Location**: `python/victory/plugins/<language>/`

**Structure**:
```python
# __init__.py
from .executor import TestExecutor
from .parser import CodeParser
from .formatter import CodeFormatter

__all__ = ["TestExecutor", "CodeParser", "CodeFormatter"]
```

**Implementation**:
```python
# executor.py
from victory.core.executor import TestExecutor, TestResult

class GoTestExecutor(TestExecutor):
    """Execute Go tests with 'go test ./...'"""
    
    async def detect(self) -> bool:
        """Return True if Go repo detected"""
        return Path("go.mod").exists()
    
    async def run(self, path: str) -> TestSuiteResult:
        """Execute tests and return results"""
        result = await subprocess.run(
            ["go", "test", "-v", "./..."],
            cwd=path,
            capture_output=True
        )
        return self.parse_output(result.stdout)
    
    def parse_output(self, output: str) -> TestSuiteResult:
        """Parse 'go test' output"""
        # Parse and return TestSuiteResult
        pass
```

**Registration** (`python/victory/core/executor/executor.py`):
```python
from victory.plugins.go import GoTestExecutor

class TestExecutor:
    EXECUTORS = {
        "python": PytestExecutor,
        "javascript": JestExecutor,
        "go": GoTestExecutor,  # ← Add here
    }
    
    async def detect_framework(self) -> Optional[str]:
        for name, executor_class in self.EXECUTORS.items():
            if await executor_class().detect():
                return name
        return None
```

### 2. VCS Plugins

Support new version control systems.

**Example: GitLab Support**

```python
# python/victory/plugins/vcs/gitlab.py
from victory.core.github import GitHubClient  # Base class

class GitLabClient(GitHubClient):
    """GitLab API client"""
    
    def __init__(self, token: str, base_url: str = "https://gitlab.com"):
        self.token = token
        self.base_url = base_url
    
    async def fetch_issue(self, issue_id: int) -> Issue:
        """Fetch GitLab issue"""
        url = f"{self.base_url}/api/v4/projects/.../issues/{issue_id}"
        return await self.client.get(url)
    
    async def create_pr(self, **kwargs) -> PR:
        """Create merge request (GitLab's PR equivalent)"""
        pass
```

**Registration**:
```python
# python/victory/core/github/__init__.py
from victory.plugins.vcs.gitlab import GitLabClient

VCS_PROVIDERS = {
    "github": GitHubClient,
    "gitlab": GitLabClient,  # ← Add
}

def create_vcs_client(vcs_type: str, **kwargs):
    return VCS_PROVIDERS[vcs_type](**kwargs)
```

### 3. CI/CD Plugins

Integrate with CI/CD platforms.

**Example: Jenkins Integration**

```python
# python/victory/plugins/ci/jenkins.py
import httpx

class JenkinsCI:
    """Jenkins CI client"""
    
    def __init__(self, url: str, token: str):
        self.url = url
        self.client = httpx.AsyncClient(
            auth=httpx.BasicAuth("victory", token)
        )
    
    async def trigger_build(self, job_name: str) -> str:
        """Trigger Jenkins job"""
        url = f"{self.url}/job/{job_name}/build"
        resp = await self.client.post(url)
        return resp.headers["Location"]  # Build URL
    
    async def get_build_status(self, build_url: str) -> str:
        """Get build status (SUCCESS, FAILURE, etc.)"""
        api_url = f"{build_url}/api/json"
        resp = await self.client.get(api_url)
        return resp.json()["result"]
    
    async def wait_for_build(self, build_url: str, timeout: int = 3600):
        """Wait for build to complete"""
        start = time.time()
        while time.time() - start < timeout:
            status = await self.get_build_status(build_url)
            if status in ["SUCCESS", "FAILURE", "ABORTED"]:
                return status
            await asyncio.sleep(10)  # Poll every 10s
        raise TimeoutError("Build took too long")
```

**Usage**:
```python
# In agent loop
jenkins = JenkinsCI("https://jenkins.example.com", token)
build_url = await jenkins.trigger_build("victory-tests")
status = await jenkins.wait_for_build(build_url)
if status == "SUCCESS":
    print("CI passed!")
```

##  Creating a Custom Plugin

### Step 1: Define Plugin Interface

```python
# python/victory/plugins/my_lang/executor.py
from abc import ABC, abstractmethod
from victory.core.executor import TestSuiteResult

class MyLangExecutor(ABC):
    """Base class for my language test executor"""
    
    @abstractmethod
    async def detect(self) -> bool:
        """Check if this language is present"""
        pass
    
    @abstractmethod
    async def run(self, path: str) -> TestSuiteResult:
        """Run tests and return results"""
        pass
    
    @abstractmethod
    def parse_output(self, output: str) -> TestSuiteResult:
        """Parse test output"""
        pass
```

### Step 2: Implement Plugin

```python
# python/victory/plugins/python_rust/executor.py
import subprocess
from pathlib import Path
from victory.plugins.my_lang.executor import MyLangExecutor

class PythonRustExecutor(MyLangExecutor):
    """Pytest + cargo test executor"""
    
    async def detect(self) -> bool:
        """Detect if Python+Rust project"""
        return (
            Path("Cargo.toml").exists() and
            (Path("tests") / "test_*.py").glob("*")
        )
    
    async def run(self, path: str) -> TestSuiteResult:
        """Run both pytest and cargo test"""
        # Run pytest
        py_result = await self._run_pytest(path)
        
        # Run cargo test
        rs_result = await self._run_cargo(path)
        
        # Combine results
        return TestSuiteResult(
            framework="python+rust",
            total=py_result.total + rs_result.total,
            passed=py_result.passed + rs_result.passed,
            failed=py_result.failed + rs_result.failed,
        )
    
    async def _run_pytest(self, path: str):
        # Implementation
        pass
    
    async def _run_cargo(self, path: str):
        # Implementation
        pass
    
    def parse_output(self, output: str):
        # Implementation
        pass
```

### Step 3: Register Plugin

```python
# python/victory/core/executor/executor.py
from victory.plugins.python_rust.executor import PythonRustExecutor

class TestExecutor:
    EXECUTORS = {
        "python": PytestExecutor,
        "javascript": JestExecutor,
        "go": GoTestExecutor,
        "python+rust": PythonRustExecutor,  # ← Add
    }
```

### Step 4: Test Plugin

```python
# tests/test_python_rust_plugin.py
import pytest
from victory.plugins.python_rust.executor import PythonRustExecutor

@pytest.mark.asyncio
async def test_detect_python_rust():
    executor = PythonRustExecutor()
    # Create test directory with Cargo.toml and tests/
    result = await executor.detect()
    assert result is True

@pytest.mark.asyncio
async def test_run_tests():
    executor = PythonRustExecutor()
    result = await executor.run("/path/to/repo")
    assert result.total > 0
```

##  Packaging Plugins

### As Separate Package

```python
# setup.py (for plugin package)
from setuptools import setup

setup(
    name="victory-plugin-kotlin",
    version="0.1.0",
    py_modules=["victory_kotlin"],
    install_requires=[
        "victory>=0.2.0",
    ],
    entry_points={
        "victory.plugins": [
            "kotlin = victory_kotlin:KotlinExecutor",
        ]
    }
)
```

### Load External Plugins

```python
# python/victory/core/executor/executor.py
import importlib

class TestExecutor:
    def __init__(self):
        self.executors = self._load_plugins()
    
    def _load_plugins(self):
        """Load plugins from entry points"""
        plugins = {}
        try:
            import pkg_resources
            for entry_point in pkg_resources.iter_entry_points("victory.plugins"):
                plugins[entry_point.name] = entry_point.load()
        except:
            pass
        return plugins
```

##  Plugin Examples

### Complete Python Plugin

```python
#python/victory/plugins/django/executor.py
class DjangoTestExecutor:
    """Django test executor"""
    
    async def detect(self) -> bool:
        return (
            Path("manage.py").exists() and
            Path("settings.py").exists()
        )
    
    async def run(self, path: str) -> TestSuiteResult:
        result = await subprocess.run(
            ["python", "manage.py", "test", "-v", "2"],
            cwd=path,
            capture_output=True
        )
        
        from victory.core.executor import TestSuiteResult, TestStatus
        
        # Parse Django test output
        output = result.stdout.decode()
        lines = output.split('\n')
        
        # Look for summary line: "Ran 42 tests..."
        passed = 0
        failed = 0
        for line in lines:
            if "OK" in line:
                passed += 42  # Simplified
            elif "FAILED" in line:
                # Parse failures
                pass
        
        return TestSuiteResult(
            framework="django",
            total=42,
            passed=passed,
            failed=failed,
        )
    
    def parse_output(self, output: str):
        pass
```

### Custom Code Parser Plugin

```python
# python/victory/plugins/kotlin/parser.py
import re
from dataclasses import dataclass

@dataclass
class KotlinFunction:
    name: str
    args: List[str]
    return_type: str

class KotlinParser:
    """Parse Kotlin code for analysis"""
    
    def parse_functions(self, source: str) -> List[KotlinFunction]:
        """Extract functions from Kotlin source"""
        pattern = r'fun\s+(\w+)\s*\((.*?)\)\s*:\s*(\w+)'
        matches = re.finditer(pattern, source)
        
        functions = []
        for match in matches:
            func = KotlinFunction(
                name=match.group(1),
                args=[a.strip() for a in match.group(2).split(',')],
                return_type=match.group(3)
            )
            functions.append(func)
        
        return functions
```

##  Plugin Development Checklist

- [ ] Inherit from appropriate base class
- [ ] Implement all abstract methods
- [ ] Add comprehensive docstrings
- [ ] Write unit tests
- [ ] Test with real projects
- [ ] Handle errors gracefully
- [ ] Document setup requirements
- [ ] Register in appropriate manager
- [ ] Add to plugin registry
- [ ] Submit PR or publish package

##  Useful Resources

- Base classes: See `python/victory/core/*/` modules
- Examples: Check ExistingPlugins in `python/victory/plugins/`
- Testing: Use pytest with async support
- Async/await: Python 3.7+ syntax

---

**See Also:**
- [DEVELOPMENT.md](DEVELOPMENT.md) - Dev environment setup
- [MODULES.md](MODULES.md) - Module documentation
- [LLM_INTEGRATION.md](LLM_INTEGRATION.md) - Add new LLM providers
