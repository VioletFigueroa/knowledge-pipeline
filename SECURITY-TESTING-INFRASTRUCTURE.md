# Security & Testing Infrastructure Task List

**Context**: Generated Python code requiring security hardening, testing infrastructure, and FOSS-ready standards before sharing or extension development.

**Status**: Planning Phase  
**Priority**: Critical (Complete before public release)  
**Timeline**: 2-3 weeks implementation

---

## PHASE 1: FOUNDATION (Days 1-3)

### 1.1 Git & Version Control Setup ⭐ START HERE

**Why**: Version control is foundational for everything else; enables rollback, tracking, collaboration.

**Tasks**:
- [ ] Initialize git repository: `git init`
- [ ] Create `.gitignore` file:
  - `__pycache__/`, `*.pyc`, `*.pyo`
  - `.venv/`, `venv/`, `.env`
  - `*.csv` (intermediate outputs)
  - `.pytest_cache/`, `.coverage`
  - `*.log`, `debug/`
  - IDE files: `.vscode/`, `.idea/`
- [ ] Create `CHANGELOG.md` with version tracking
- [ ] Create `.git-commit-message-template` for consistent commits
- [ ] Set git config: 
  - `git config user.name "Your Name"`
  - `git config user.email "your@email.com"`
- [ ] Make initial commit: "Initial: Batch import system with 5 stages"

**Validation**:
```bash
git log --oneline  # Shows first commit
git status         # Clean working directory
```

**Deliverable**: Clean git repo with version history

---

### 1.2 Project Structure & Organization

**Why**: Proper structure enables testing, distribution, and maintenance.

**Tasks**:
- [ ] Create standardized directory structure:
```
batch-import-system/
├── .github/
│   └── workflows/          # CI/CD pipelines
├── .gitignore
├── src/                    # Source code (rename from scripts/)
│   ├── __init__.py
│   ├── orchestrate_import.py
│   ├── stage_*.py          # All 5 stage modules
│   ├── config.json
│   ├── dictionaries/
│   ├── schemas/
│   └── utils/              # Helper modules
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_stage_1.py
│   ├── test_stage_2.py
│   ├── test_stage_3.py
│   ├── test_stage_4.py
│   ├── test_stage_5.py
│   ├── test_integration.py
│   ├── fixtures/           # Test data
│   └── conftest.py         # Pytest configuration
├── docs/                   # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   └── SECURITY.md
├── examples/               # Example usage
│   ├── basic_import.py
│   └── sample_data/
├── requirements.txt        # Python dependencies
├── setup.py                # Package setup
├── pyproject.toml          # Modern Python packaging
├── pytest.ini              # Pytest config
├── .pylintrc               # Pylint config
├── .flake8                 # Flake8 config
├── .bandit                 # Bandit config
├── tox.ini                 # Tox multi-version testing
├── Makefile                # Common tasks
├── LICENSE                 # FOSS license (MIT/Apache-2.0)
├── README.md               # Main documentation
├── CHANGELOG.md            # Version history
├── CODE_OF_CONDUCT.md      # Community guidelines
├── SECURITY.md             # Security policy
├── CONTRIBUTING.md         # Contribution guidelines
└── MAINTAINERS.md          # Maintainer info
```

- [ ] Move existing code: `mv scripts/ src/`
- [ ] Create `src/__init__.py` with version: `__version__ = "0.1.0-alpha"`
- [ ] Create `tests/` directory structure
- [ ] Create `docs/` directory with template files

**Validation**:
```bash
ls -la src/        # All modules present
ls -la tests/      # Test directory exists
```

**Deliverable**: Organized, professional project structure

---

### 1.3 Dependencies & Virtual Environment

**Why**: Reproducible, isolated environment prevents dependency hell.

**Tasks**:
- [ ] Create `requirements.txt` with pinned versions:
```
pyyaml==6.0.1
pandas==2.1.4
pyspellchecker==0.7.0
python-dotenv==1.0.0
requests==2.31.0
```

- [ ] Create `requirements-dev.txt` for development:
```
pytest==7.4.3
pytest-cov==4.1.0
pytest-xdist==3.5.0
black==23.12.0
flake8==6.1.0
pylint==3.0.3
mypy==1.7.1
bandit==1.7.5
safety==2.3.5
tox==4.11.3
sphinx==7.2.6
sphinx-rtd-theme==2.0.0
```

- [ ] Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

- [ ] Create `.env.example`:
```
LOG_LEVEL=INFO
BATCH_SIZE=50
MAX_FILE_SIZE=5000000
DEBUG=False
```

- [ ] Test imports: `python -c "import yaml, pandas, pyspellchecker"`

**Validation**:
```bash
pip list | grep -E "pytest|pylint|bandit"  # All tools installed
which pytest                               # Tools in PATH
```

**Deliverable**: Clean, reproducible environment with all dependencies pinned

---

## PHASE 2: STATIC ANALYSIS (Days 4-6)

### 2.1 Setup Code Linting & Formatting

**Why**: Consistent code style prevents bugs, improves readability, catches common errors.

**Tools**: Black (formatter), Flake8 (linter), Pylint (deeper analysis)

**Tasks**:

#### Black (Code Formatting)
- [ ] Create `black` configuration in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.git
  | __pycache__
  | \.venv
)/
'''
```

- [ ] Format all code: `black src/ tests/`
- [ ] Check formatting without changes: `black --check src/`

#### Flake8 (PEP8 Compliance)
- [ ] Create `.flake8` config:
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv
ignore = E203,W503
per-file-ignores =
    __init__.py:F401
    tests/*:F401,F811
```

- [ ] Run linter: `flake8 src/`
- [ ] Fix issues: Address all warnings

#### Pylint (Advanced Analysis)
- [ ] Create `.pylintrc` config: `pylint --generate-rcfile > .pylintrc`
- [ ] Customize settings:
  - Max line length: 100
  - Min similarity: 4
  - Disable: `line-too-long` (handled by Black)
- [ ] Run: `pylint src/` and address critical/error issues
- [ ] Aim for score: > 8.0/10

**Validation**:
```bash
black --check src/        # All files formatted
flake8 src/ --count      # Count issues (should be 0-5)
pylint src/ --exit-zero  # Score displayed
```

**Deliverable**: Clean, consistently formatted codebase

---

### 2.2 Type Checking with MyPy

**Why**: Catches type errors before runtime, improves IDE support, documents intent.

**Tasks**:
- [ ] Create `mypy.ini`:
```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Too strict initially
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
```

- [ ] Add type annotations to key functions:
```python
from typing import Dict, List, Optional, Tuple
from pathlib import Path

def identify_files(source_dir: Path) -> List[Path]:
    """Scan directory and return list of markdown files."""
    ...

def build_layer1_frontmatter_dict(
    filename: str, 
    source_type: str,
    batch_id: str
) -> Dict[str, any]:
    """Build Layer 1 frontmatter structure."""
    ...

def validate_layer1(file_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate Layer 1 structure. Returns (is_valid, error_message)."""
    ...
```

- [ ] Run mypy: `mypy src/`
- [ ] Incrementally add annotations (start with public APIs)
- [ ] Target: 80% type coverage

**Validation**:
```bash
mypy src/ --stats    # Shows coverage percentage
mypy src/ --html out/ # Generates HTML report
```

**Deliverable**: Type-annotated code with mypy configuration

---

### 2.3 Dependency Vulnerability Scanning

**Why**: Catches known vulnerabilities in dependencies before they cause issues.

**Tasks**:
- [ ] Install safety: `pip install safety`
- [ ] Scan dependencies: `safety check`
- [ ] Create GitHub issue for any HIGH/CRITICAL
- [ ] Set up auto-update policy for dependencies

- [ ] Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    allow:
      - dependency-type: "all"
    pull-requests:
      auto-merge: false
```

**Validation**:
```bash
safety check --json    # All dependencies safe
```

**Deliverable**: Dependency security scanning configured

---

### 2.4 Security Scanning with Bandit

**Why**: Detects common security issues: hardcoded passwords, SQL injection, insecure functions.

**Tasks**:
- [ ] Create `.bandit` config:
```yaml
# .bandit
tests:
  - B201
  - B301
  - B302
  - B303
  - B304
  - B305
  - B306
  - B307
  - B308
  - B309
  - B310
  - B311
  - B312
  - B313
  - B314
  - B315
  - B316
  - B317
  - B318
  - B319
  - B320
  - B321
  - B322
  - B323
  - B324
  - B325

assert_used:
  skips: []

hardcoded_sql_string:
  skips: []

hardcoded_tmp_directory:
  skips: []
```

- [ ] Run bandit: `bandit -r src/`
- [ ] Fix critical security issues
- [ ] Document any skips with `# nosec` comments

- [ ] Address common issues:
  - [ ] No hardcoded credentials (use `.env`)
  - [ ] Use `subprocess.run()` safely (no shell=True)
  - [ ] Validate all file paths (prevent directory traversal)
  - [ ] Use `tempfile` for temp files, not `/tmp`
  - [ ] Sanitize user inputs

**Example Fix**:
```python
# ❌ BEFORE: Vulnerable
import subprocess
output = subprocess.run(f"process {file}", shell=True)

# ✅ AFTER: Secure
import subprocess
output = subprocess.run(["process", file], shell=False)
```

**Validation**:
```bash
bandit -r src/ --json > bandit-report.json
cat bandit-report.json | jq '.results[] | .severity'  # All MEDIUM or lower
```

**Deliverable**: Security scanning with bandit, critical issues fixed

---

## PHASE 3: TESTING INFRASTRUCTURE (Days 7-12)

### 3.1 Unit Testing Framework Setup

**Why**: Automated tests catch regressions, ensure code works as designed, improve refactoring confidence.

**Tasks**:
- [ ] Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    security: Security-related tests
```

- [ ] Create `tests/conftest.py`:
```python
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Provide temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)

@pytest.fixture
def sample_markdown_file(temp_dir):
    """Provide sample markdown file."""
    content = """# Test Document

This is a test document for testing.

## Tags
- #tag1
- #tag2
"""
    file = temp_dir / "test.md"
    file.write_text(content)
    return file

@pytest.fixture
def config():
    """Provide test configuration."""
    return {
        "max_file_size": 5000000,
        "batch_size": 50,
        "debug": True
    }
```

- [ ] Create test file: `tests/test_stage_1.py`
```python
import pytest
from src.stage_1_quality_assurance import identify_files, lint_markdown

@pytest.mark.unit
def test_identify_files_finds_markdown(temp_dir, sample_markdown_file):
    """Test that identify_files finds markdown files."""
    files = identify_files(temp_dir)
    assert len(files) == 1
    assert files[0].name == "test.md"

@pytest.mark.unit
def test_lint_markdown_detects_trailing_whitespace(temp_dir):
    """Test that linter detects trailing whitespace."""
    file = temp_dir / "bad.md"
    file.write_text("# Title  \n")  # Trailing spaces
    
    linter = MarkdownLinter()
    errors = linter.lint(file)
    
    assert any("trailing" in str(e).lower() for e in errors)
```

**Validation**:
```bash
pytest tests/ -v                    # Run all tests
pytest tests/ --cov=src            # With coverage
pytest tests/ -k "test_identify"    # Run specific test
```

**Deliverable**: Pytest configuration with fixtures and sample tests

---

### 3.2 Unit Tests for Each Stage

**Why**: Each module needs validation to ensure it works correctly in isolation.

**Create `tests/test_stage_*.py` files**:

#### test_stage_1.py (Quality Assurance)
- [ ] Test `identify_files()`:
  - Finds markdown files in directory
  - Handles nested directories
  - Ignores non-markdown files
  - Handles empty directory
  
- [ ] Test `MarkdownLinter`:
  - Detects heading hierarchy errors
  - Detects list inconsistencies
  - Detects trailing whitespace
  - Detects extra blank lines
  - Auto-fixes fixable issues
  - Handles edge cases (empty files, no headings)

- [ ] Test `normalize_spelling()`:
  - Corrects common misspellings
  - Doesn't flag technical terms
  - Handles hyphenated words
  - Preserves code blocks

- [ ] Test `extract_existing_metadata()`:
  - Extracts YAML frontmatter
  - Extracts properties syntax
  - Extracts inline metadata
  - Handles missing metadata

**Example**:
```python
@pytest.mark.unit
class TestMarkdownLinter:
    def test_heading_hierarchy(self, temp_dir):
        file = temp_dir / "bad_hierarchy.md"
        file.write_text("# Title\n### Skipped h2\n## Proper h2")
        
        linter = MarkdownLinter()
        errors = linter.lint(file)
        
        assert len(errors) > 0
        assert any("heading" in str(e).lower() for e in errors)
    
    def test_auto_fix_trailing_whitespace(self, temp_dir):
        file = temp_dir / "trailing.md"
        file.write_text("# Title  \n")
        
        linter = MarkdownLinter()
        linter.fix(file)
        
        content = file.read_text()
        assert not content.endswith("  \n")
```

#### test_stage_2.py (Layer 1 Metadata)
- [ ] Test `parse_lighthouse_path()`:
  - Extracts course, week, topic
  - Handles various path formats
  - Validates date parsing
  
- [ ] Test `build_layer1_frontmatter_dict()`:
  - Creates valid YAML structure
  - Sets correct source type
  - Calculates ISO week
  - Includes batch ID

- [ ] Test `apply_layer1_to_file()`:
  - Prepends frontmatter
  - Preserves original content
  - Validates output format

#### test_stage_3.py (Layer 2 Tagging)
- [ ] Test `KeywordExtractor`:
  - Extracts keywords from content
  - Filters common words
  - Identifies multi-word terms
  - Handles edge cases

- [ ] Test `TagMapper`:
  - Maps to all 8 dimensions
  - Validates tag format
  - Handles missing dimensions
  - Applies tags to file

#### test_stage_4.py (Layer 3 Placeholders)
- [ ] Test `detect_layer3_connections()`:
  - Finds prerequisite keywords
  - Finds enable keywords
  - Generates suggestions

- [ ] Test `build_layer3_placeholders()`:
  - Creates markdown sections
  - Validates section format
  - Handles existing sections

#### test_stage_5.py (Validation)
- [ ] Test `validate_file_integrity()`:
  - Checks frontmatter completeness
  - Validates tag structure
  - Checks UTF-8 encoding
  - Verifies file size

- [ ] Test `validate_batch_consistency()`:
  - Detects duplicates
  - Validates batch IDs
  - Checks date ranges

**Target**: 85%+ code coverage

**Validation**:
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html    # View coverage report
```

**Deliverable**: Comprehensive unit tests with 85%+ coverage

---

### 3.3 Integration Tests

**Why**: Ensures all stages work together correctly end-to-end.

**Create `tests/test_integration.py`**:

```python
@pytest.mark.integration
class TestFullPipeline:
    def test_complete_pipeline_execution(self, temp_dir):
        """Test complete 5-stage pipeline on sample files."""
        # Setup
        create_sample_files(temp_dir, count=5)
        
        # Execute
        orchestrator = ImportOrchestrator(
            source_dir=temp_dir,
            source_type="test",
            batch_id="integration-test-1",
            output_dir=temp_dir / "output"
        )
        
        # Run pipeline
        result = orchestrator.run()
        
        # Validate
        assert result.success
        assert result.files_processed == 5
        assert result.stage_1_pass_rate > 0.9
        assert result.stage_2_pass_rate > 0.9
        
        # Check outputs
        output_dir = temp_dir / "output"
        assert (output_dir / "stage_1_qa").exists()
        assert (output_dir / "stage_2_metadata").exists()
        assert (output_dir / "import-batch-report.md").exists()

    def test_lighthouse_labs_import_workflow(self, temp_dir):
        """Test Lighthouse Labs specific workflow."""
        # Create realistic LL files
        create_lighthouse_labs_samples(temp_dir)
        
        # Process
        orchestrator = ImportOrchestrator(
            source_dir=temp_dir,
            source_type="lighthouse_labs",
            batch_id="ll-batch-1"
        )
        result = orchestrator.run()
        
        # Verify
        assert result.success
        assert all(f.metadata.source == "lighthouse_labs" for f in result.processed_files)

    @pytest.mark.slow
    def test_large_batch_performance(self, temp_dir):
        """Test performance with 100+ files."""
        create_sample_files(temp_dir, count=100)
        
        start = time.time()
        orchestrator = ImportOrchestrator(temp_dir, "test", "perf-test")
        result = orchestrator.run()
        elapsed = time.time() - start
        
        # Should complete within time budget
        assert elapsed < 300  # 5 minutes for 100 files
        assert result.success
```

**Validation**:
```bash
pytest tests/test_integration.py -v -s
pytest tests/ -m integration  # Run only integration tests
```

**Deliverable**: End-to-end integration tests

---

### 3.4 Performance & Stress Testing

**Why**: Ensures system handles production loads without degradation.

**Create `tests/test_performance.py`**:

```python
import pytest
import time
from src.orchestrate_import import ImportOrchestrator

@pytest.mark.slow
class TestPerformance:
    def test_stage_1_performance_100_files(self, temp_dir):
        """Stage 1 should process 100 files in < 30 seconds."""
        create_sample_files(temp_dir, count=100)
        
        start = time.time()
        from src.stage_1_quality_assurance import identify_files
        files = identify_files(temp_dir)
        elapsed = time.time() - start
        
        assert len(files) == 100
        assert elapsed < 30

    def test_stage_3_tagging_memory_usage(self, temp_dir):
        """Test memory usage doesn't balloon with large files."""
        create_large_sample_files(temp_dir, count=50, size_mb=2)
        
        # Memory monitoring
        import tracemalloc
        tracemalloc.start()
        
        from src.stage_3_layer2_tagging import KeywordExtractor
        extractor = KeywordExtractor()
        for file in temp_dir.glob("*.md"):
            extractor.extract_keywords(file.read_text())
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Should not exceed 500MB
        assert peak / 1024 / 1024 < 500

    def test_concurrent_processing_stress(self, temp_dir):
        """Test system handles concurrent requests."""
        from concurrent.futures import ThreadPoolExecutor
        
        create_sample_files(temp_dir, count=20)
        
        def process_file(file):
            from src.stage_1_quality_assurance import lint_markdown
            linter = MarkdownLinter()
            return linter.lint(file)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            files = list(temp_dir.glob("*.md"))
            results = list(executor.map(process_file, files))
        
        assert len(results) == 20
        assert all(isinstance(r, list) for r in results)
```

**Validation**:
```bash
pytest tests/test_performance.py -v -s
pytest tests/ -m slow --durations=10  # Slowest tests
```

**Deliverable**: Performance benchmarks and stress testing

---

## PHASE 4: DYNAMIC TESTING (DAST) (Days 13-15)

### 4.1 Input Validation Testing

**Why**: Tests that invalid inputs don't cause crashes or security issues.

**Create `tests/test_input_validation.py`**:

```python
import pytest
from pathlib import Path
from src.stage_1_quality_assurance import identify_files

@pytest.mark.unit
class TestInputValidation:
    def test_identify_files_invalid_path(self):
        """Test behavior with non-existent path."""
        with pytest.raises(FileNotFoundError):
            identify_files(Path("/nonexistent/path"))
    
    def test_identify_files_permission_denied(self, temp_dir):
        """Test handling of permission errors."""
        restricted = temp_dir / "restricted"
        restricted.mkdir()
        restricted.chmod(0o000)
        
        try:
            with pytest.raises(PermissionError):
                identify_files(restricted)
        finally:
            restricted.chmod(0o755)
    
    def test_layer1_invalid_date_format(self):
        """Test handling of malformed dates."""
        from src.stage_2_layer1_metadata import validate_layer1
        
        frontmatter = """---
date: "not-a-date"
---"""
        
        is_valid, error = validate_layer1(frontmatter)
        assert not is_valid
        assert "date" in error.lower()
    
    def test_tag_injection_attempt(self, temp_dir):
        """Test that malicious tag content is sanitized."""
        from src.stage_3_layer2_tagging import TagMapper
        
        malicious_content = """
        # Title
        This contains <script>alert('xss')</script> content
        """
        
        mapper = TagMapper()
        tags = mapper.map_keywords_to_tags(malicious_content)
        
        # No script tags should be present
        assert not any("<script>" in str(t) for t in tags)
    
    def test_path_traversal_attempt(self, temp_dir):
        """Test that ../ path traversal is prevented."""
        from src.stage_1_quality_assurance import normalize_path
        
        malicious = "../../../etc/passwd"
        safe_path = normalize_path(malicious, temp_dir)
        
        assert safe_path.is_relative_to(temp_dir)
    
    def test_huge_file_handling(self, temp_dir):
        """Test handling of extremely large files."""
        from src.stage_1_quality_assurance import identify_files
        from src.config import MAX_FILE_SIZE
        
        huge_file = temp_dir / "huge.md"
        # Create file larger than max
        with open(huge_file, 'w') as f:
            f.write("x" * (MAX_FILE_SIZE + 1000))
        
        files = identify_files(temp_dir)
        
        # Should either skip or handle gracefully
        assert len(files) == 0 or files[0].stat().st_size < MAX_FILE_SIZE
    
    def test_special_characters_in_filename(self, temp_dir):
        """Test handling of special characters."""
        from src.stage_1_quality_assurance import identify_files
        
        special_file = temp_dir / "файл🚀with-special-chars.md"
        special_file.write_text("# Test")
        
        files = identify_files(temp_dir)
        assert len(files) == 1
```

**Validation**:
```bash
pytest tests/test_input_validation.py -v
```

**Deliverable**: Input validation test suite

---

### 4.2 Error Handling & Recovery Testing

**Why**: Ensures graceful degradation under adverse conditions.

```python
@pytest.mark.unit
class TestErrorHandling:
    def test_stage_1_continues_on_single_file_error(self, temp_dir):
        """Pipeline continues even if one file fails QA."""
        # Create 10 files, one will fail
        for i in range(10):
            if i == 5:
                # Create problematic file
                (temp_dir / f"bad_{i}.md").write_bytes(b'\xff\xfe invalid utf-8')
            else:
                (temp_dir / f"good_{i}.md").write_text("# File " + str(i))
        
        results = identify_files_with_errors(temp_dir)
        
        # Should process 9 successfully
        assert results.successful == 9
        assert results.failed == 1
        assert results.continue_on_error == True
    
    def test_corrupted_config_handling(self, temp_dir):
        """Gracefully handle corrupted config file."""
        from src.config import load_config
        
        config_file = temp_dir / "bad_config.json"
        config_file.write_text("{invalid json")
        
        # Should raise descriptive error
        with pytest.raises(ConfigError) as exc:
            load_config(config_file)
        
        assert "Invalid JSON" in str(exc.value)
    
    def test_missing_required_field_recovery(self):
        """Test recovery when required field missing."""
        from src.stage_2_layer1_metadata import validate_layer1
        
        incomplete_frontmatter = """---
source: lighthouse_labs
---"""
        
        # Should validate and report missing field
        is_valid, errors = validate_layer1(incomplete_frontmatter)
        assert not is_valid
        assert "batch_id" in errors or "date" in errors
```

**Deliverable**: Comprehensive error handling tests

---

## PHASE 5: DOCUMENTATION FOR FOSS (Days 16-18)

### 5.1 Security Policy & Vulnerability Disclosure

**Create `SECURITY.md`**:

```markdown
# Security Policy

## Reporting Security Vulnerabilities

DO NOT open a public GitHub issue for security vulnerabilities.

Instead, email security@yourproject.dev with:
- Description of vulnerability
- Affected versions
- Proof of concept (if possible)
- Suggested fix (if you have one)

We will:
1. Acknowledge receipt within 48 hours
2. Provide assessment within 1 week
3. Release fix within 2-4 weeks
4. Credit you (unless you request anonymity)

## Security Standards

This project follows:
- OWASP Top 10 for security best practices
- CWE/SANS Top 25 for common weakness enumeration
- NIST guidelines for secure development

## Scanning Tools

All code undergoes:
- Bandit (security linting)
- Safety (dependency vulnerability scanning)
- MyPy (type checking)
- Regular penetration testing

## Supported Versions

| Version | Status | Until |
|---------|--------|-------|
| 1.0.x | Supported | - |
| 0.x.x | Security fixes only | 2025-12-31 |

## Security Checklist

- [x] No hardcoded credentials
- [x] Input validation on all user input
- [x] Path traversal protection
- [x] SQL injection protection (N/A)
- [x] XSS protection
- [x] CSRF protection (N/A)
- [x] Secure defaults
- [x] Error handling (no info leakage)
```

**Deliverable**: Public security policy

---

### 5.2 Contributing Guidelines for Code Review

**Create/Update `CONTRIBUTING.md`**:

```markdown
# Contributing Guidelines

## Code Quality Standards

All pull requests must meet these standards:

### 1. Testing (Required)
- Minimum 85% code coverage
- All new features have tests
- All tests pass: `pytest tests/`
- No regressions detected

### 2. Security (Required)
- Passes security scan: `bandit -r src/`
- No hardcoded credentials
- Validates all inputs
- Type checked: `mypy src/`

### 3. Code Style (Required)
- Formatted with Black: `black src/`
- No linting errors: `flake8 src/`
- Pylint score > 8.0: `pylint src/`
- Docstrings on all public functions

### 4. Documentation (Required)
- Update CHANGELOG.md
- Update README.md if needed
- Update docstrings
- Add comments for complex logic

## Development Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes with tests
4. Run quality checks:
   ```bash
   black src/ tests/
   flake8 src/ tests/
   pylint src/ tests/
   mypy src/
   pytest tests/ --cov=src
   bandit -r src/
   ```
5. Update CHANGELOG.md
6. Commit with descriptive message
7. Push to fork
8. Open pull request

## Commit Message Format

```
[TYPE] Brief description (max 72 chars)

Longer explanation of changes (wrap at 72 chars)

- Bullet point 1
- Bullet point 2

Fixes #123
```

Types: feature, fix, docs, test, refactor, perf, security, ci

## Code Review Checklist

Reviewers will verify:
- [ ] Tests pass (85%+ coverage)
- [ ] No security issues
- [ ] Code style compliant
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows architecture patterns
```

**Deliverable**: Professional contributing guidelines

---

### 5.3 Architecture & Design Documentation

**Create `docs/ARCHITECTURE.md`**:

```markdown
# Architecture & Design

## System Overview

The batch import system consists of 5 independent stages:

```
Files → Stage 1 (QA) → Stage 2 (L1 Metadata) → Stage 3 (L2 Tags) 
  → Stage 4 (L3 Placeholders) → Stage 5 (Validation) → Output
```

## Stage Responsibilities

### Stage 1: Quality Assurance
- Identifies markdown files
- Lints markdown formatting
- Spell checks content
- Extracts existing metadata
- Auto-fixes where possible

### Stage 2: Layer 1 Metadata
- Parses source hierarchy
- Generates YAML frontmatter
- Calculates dates & ISO weeks
- Maps to Logseq structure

... (continue for all stages)

## Design Principles

1. **Separation of Concerns**: Each stage handles one aspect
2. **Reusability**: Stages can run independently
3. **Extensibility**: New sources via parsers
4. **Observability**: Comprehensive logging & reporting
5. **Safety**: Comprehensive validation & rollback
```

**Deliverable**: Complete architecture documentation

---

### 5.4 Testing Strategy Document

**Create `docs/TESTING.md`**:

```markdown
# Testing Strategy

## Test Types

### Unit Tests (70% of test time)
- Test individual functions
- Use fixtures for reusable setup
- Mock external dependencies
- Located in `tests/test_stage_*.py`

### Integration Tests (20% of test time)
- Test multiple components together
- Use real files and directories
- Test full pipeline
- Located in `tests/test_integration.py`

### Performance Tests (10% of test time)
- Test with realistic loads
- Monitor memory and time
- Stress test with edge cases
- Located in `tests/test_performance.py`

## Coverage Requirements

- Minimum 85% code coverage
- 100% coverage for security-critical code
- All public APIs tested

## Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific type
pytest tests/ -m unit
pytest tests/ -m integration

# Performance (slow)
pytest tests/ -m slow
```

## Testing Checklist Before Commit

- [ ] All tests pass
- [ ] Coverage > 85%
- [ ] No flaky tests
- [ ] Performance acceptable
```

**Deliverable**: Complete testing documentation

---

## PHASE 6: CI/CD PIPELINE (Days 19-21)

### 6.1 GitHub Actions Setup

**Create `.github/workflows/tests.yml`**:

```yaml
name: Tests & Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with Black
      run: black --check src tests
    
    - name: Lint with Flake8
      run: flake8 src tests
    
    - name: Lint with Pylint
      run: pylint src tests --fail-under=8.0
    
    - name: Type check with MyPy
      run: mypy src
    
    - name: Security scan with Bandit
      run: bandit -r src --format json -o bandit-report.json
      continue-on-error: true
    
    - name: Dependency scan with Safety
      run: safety check --json
      continue-on-error: true
    
    - name: Run tests with coverage
      run: pytest tests --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        fail_ci_if_error: true
    
    - name: Archive reports
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: reports-${{ matrix.os }}-${{ matrix.python-version }}
        path: |
          bandit-report.json
          coverage.xml
```

**Create `.github/workflows/security.yml`**:

```yaml
name: Security Scanning

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Bandit
      uses: gaurav-nelson/github-action-bandit@v1
      with:
        path: "src"
    
    - name: SAST with Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/python
    
    - name: Dependency check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        path: '.'
        format: 'JSON'
```

**Deliverable**: Complete CI/CD pipeline

---

### 6.2 Makefile for Local Development

**Create `Makefile`**:

```makefile
.PHONY: help install test lint format security coverage clean docs

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make coverage    - Run tests with coverage"
	@echo "  make lint        - Run all linters"
	@echo "  make format      - Format code with Black"
	@echo "  make security    - Run security checks"
	@echo "  make docs        - Generate documentation"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make all         - Install, lint, test, coverage"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

lint:
	black --check src tests
	flake8 src tests
	pylint src tests
	mypy src

format:
	black src tests
	isort src tests

security:
	bandit -r src
	safety check

docs:
	sphinx-build -b html docs/source docs/build/html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf build dist *.egg-info

all: install lint test coverage security
```

**Deliverable**: Development workflow automation

---

## PHASE 7: DEPLOYMENT & RELEASE (Days 22-23)

### 7.1 Setup.py & Package Distribution

**Create `setup.py`**:

```python
from setuptools import setup, find_packages

setup(
    name="batch-import-system",
    version="0.1.0-alpha",
    description="Batch import system for Logseq with 5-stage processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/batch-import-system",
    license="MIT",
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Python :: 3.8",
        "Python :: 3.9",
        "Python :: 3.10",
        "Python :: 3.11",
    ],
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    install_requires=[
        "pyyaml==6.0.1",
        "pandas==2.1.4",
        "pyspellchecker==0.7.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
    ],
    
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-cov==4.1.0",
            "black==23.12.0",
            "flake8==6.1.0",
            "pylint==3.0.3",
            "mypy==1.7.1",
            "bandit==1.7.5",
            "safety==2.3.5",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "batch-import=src.orchestrate_import:main",
        ]
    },
)
```

**Create `pyproject.toml`**:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "batch-import-system"
version = "0.1.0-alpha"
description = "Batch import system for Logseq"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

[tool.black]
line-length = 100

[tool.mypy]
python_version = "3.8"
warn_return_any = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Deliverable**: Python package distribution setup

---

### 7.2 Release Management

**Create `RELEASE-CHECKLIST.md`**:

```markdown
# Release Checklist

## Before Release

- [ ] All tests passing (100%)
- [ ] Coverage > 85%
- [ ] Security scan clean
- [ ] Linting clean
- [ ] Type checking clean
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] VERSION bumped
- [ ] Commit message: "Release v0.1.0"
- [ ] Git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`

## Release Process

1. Create release branch: `git checkout -b release/v0.1.0`
2. Run full test suite
3. Update version numbers
4. Update CHANGELOG.md
5. Commit & push
6. Create pull request
7. After merge:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   python -m build
   twine upload dist/*
   ```

## After Release

- [ ] Verify package on PyPI
- [ ] Create GitHub release with notes
- [ ] Update documentation
- [ ] Announce in channels
- [ ] Monitor for issues
```

**Deliverable**: Release management process

---

## FULL TASK CHECKLIST

### Phase 1: Foundation (Days 1-3) ✅
- [ ] Git setup
- [ ] Project structure
- [ ] Dependencies & venv
- **Deliverable**: Clean, organized project

### Phase 2: Static Analysis (Days 4-6) ✅
- [ ] Black + Flake8 + Pylint setup
- [ ] MyPy type checking
- [ ] Bandit security scanning
- [ ] Dependency vulnerability scanning
- **Deliverable**: Code quality baseline

### Phase 3: Testing Infrastructure (Days 7-12) ✅
- [ ] Pytest setup with fixtures
- [ ] Unit tests for all stages
- [ ] Integration tests
- [ ] Performance tests
- [ ] Input validation tests
- **Deliverable**: Comprehensive test suite (85%+ coverage)

### Phase 4: Dynamic Testing (Days 13-15) ✅
- [ ] Input validation testing
- [ ] Error handling testing
- [ ] Edge case testing
- **Deliverable**: Robust error handling

### Phase 5: FOSS Documentation (Days 16-18) ✅
- [ ] SECURITY.md
- [ ] CONTRIBUTING.md
- [ ] Architecture documentation
- [ ] Testing strategy documentation
- **Deliverable**: Professional documentation

### Phase 6: CI/CD Pipeline (Days 19-21) ✅
- [ ] GitHub Actions setup
- [ ] Multi-version testing
- [ ] Security scanning in CI
- [ ] Makefile for local dev
- **Deliverable**: Automated quality assurance

### Phase 7: Deployment & Release (Days 22-23) ✅
- [ ] Setup.py configuration
- [ ] Package distribution
- [ ] Release checklist
- **Deliverable**: Production-ready distribution

---

## SUCCESS METRICS

### Security
- ✅ Bandit score: No CRITICAL or HIGH
- ✅ Dependency scan: No known vulnerabilities
- ✅ Code review: 2 approvals required
- ✅ Security policy: Published & monitored

### Quality
- ✅ Test coverage: 85%+
- ✅ Pylint score: 8.0+
- ✅ Type coverage: 80%+
- ✅ Zero linting errors

### Reliability
- ✅ All tests pass on Python 3.8-3.11
- ✅ All tests pass on Linux, macOS, Windows
- ✅ < 0.1% failure rate in production
- ✅ All errors logged and reported

### Maintainability
- ✅ Architecture documented
- ✅ Testing strategy documented
- ✅ Contributing guidelines clear
- ✅ All functions documented

---

## IMPLEMENTATION ORDER

**Recommended approach** (if short on time):

1. **Must Have** (Week 1):
   - Phase 1: Git + Structure
   - Phase 2: Linting + Bandit
   - Phase 3: Unit tests (60%+)
   - Phase 5: README + SECURITY

2. **Should Have** (Week 2):
   - Phase 3: Full tests + coverage (85%+)
   - Phase 4: Error handling tests
   - Phase 6: Basic GitHub Actions

3. **Nice to Have** (After Release):
   - Phase 4: Performance tests
   - Phase 5: Full documentation
   - Phase 6: Advanced CI/CD

---

## TOOLS REFERENCE

| Tool | Purpose | Why |
|------|---------|-----|
| Black | Code formatting | Consistency |
| Flake8 | PEP8 linting | Standard compliance |
| Pylint | Deep analysis | Catch bugs early |
| MyPy | Type checking | Runtime error prevention |
| Bandit | Security scanning | SAST (Static App Security Test) |
| Safety | Dependency scanning | Vulnerability detection |
| Pytest | Test framework | Comprehensive testing |
| Coverage | Coverage reporting | Quality assurance |
| Pytest-xdist | Parallel testing | Faster CI |
| GitHub Actions | CI/CD | Automated quality gates |

---

## CONTINUOUS IMPROVEMENT

After initial release:

1. **Monthly Security Audits**
   - Review Bandit findings
   - Update dependency versions
   - Check for new CVEs

2. **Quarterly Code Reviews**
   - Refactor complexity hotspots
   - Update documentation
   - Improve performance

3. **Bi-Annual Architecture Review**
   - Evaluate design decisions
   - Plan major features
   - Community feedback incorporation

---

## RESOURCES

- **Security**: https://owasp.org/Top10/
- **Testing**: https://docs.pytest.org/
- **Python**: https://pep8.org/, https://peps.python.org/pep-0257/
- **FOSS**: https://opensource.guide/

---

**Status**: Ready for Implementation  
**Estimated Time**: 2-3 weeks for full implementation  
**Team Size**: 1 developer can handle if focused  
**Priority**: CRITICAL before public release  

Start with Phase 1 today! 🚀
