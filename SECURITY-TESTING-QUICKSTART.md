# Quick Start: Security & Testing Implementation

**Goal**: Get from "generated code" to "production-ready FOSS project" in minimal time  
**Time**: 2-3 weeks (can be parallelized)  
**Effort**: Mostly one-time setup, then automated

---

## WEEK 1: FOUNDATION & QUICK WINS (Days 1-5)

### Day 1: Version Control & Project Structure (2 hours)

```bash
# Initialize git
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Create directory structure
mkdir -p src tests docs .github/workflows
mkdir -p src/dictionaries src/schemas tests/fixtures

# Move existing code
mv scripts/*.py src/
mv scripts/config.json src/
mv scripts/dictionaries/* src/dictionaries/
mv scripts/schemas/* src/schemas/
rmdir scripts/

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.csv
.pytest_cache/
.coverage
htmlcov/
*.log
debug/
.vscode/
.idea/
dist/
build/
*.egg-info/
EOF

# First commit
git add .
git commit -m "Initial: Batch import system with 5 stages"
```

### Day 2: Dependencies & Linting Setup (2 hours)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install main dependencies
pip install pyyaml pandas pyspellchecker python-dotenv requests

# Install dev tools
pip install black flake8 pylint mypy pytest pytest-cov bandit safety

# Run formatters
black src/ tests/
flake8 src/ --max-line-length=100

# Fix any linting issues
pylint src/ --disable=all --enable=E

# Type check (will have errors initially - that's ok)
mypy src/ --ignore-missing-imports
```

### Day 3: First Tests & Bandit Scan (3 hours)

```bash
# Create basic test structure
mkdir -p tests/fixtures
touch tests/__init__.py tests/conftest.py

# Create conftest.py with fixtures
cat > tests/conftest.py << 'EOF'
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)

@pytest.fixture
def sample_markdown(temp_dir):
    file = temp_dir / "test.md"
    file.write_text("# Test\nContent here")
    return file
EOF

# Create first test file
touch tests/test_stage_1.py

# Run security scan
bandit -r src/ --json -o bandit-report.json
# Review output - should be minimal for new code

# Check for vulnerable dependencies
safety check
```

### Day 4: GitHub Repository Setup (1 hour)

```bash
# Create files needed for GitHub
touch LICENSE CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md

# Add license content
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy...
EOF

# Create basic README
cat > README.md << 'EOF'
# Batch Import System

Automated 5-stage import pipeline for Logseq with security & testing best practices.

## Quick Start

```bash
pip install -r requirements.txt
python src/orchestrate_import.py --source-dir ./input --batch-id import-1
```

## Testing

```bash
pytest tests/ --cov=src
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.
EOF

git add LICENSE CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md README.md
git commit -m "Docs: Add license and community guidelines"
```

### Day 5: CI/CD Pipeline Basics (2 hours)

```bash
# Create GitHub Actions workflow
mkdir -p .github/workflows

cat > .github/workflows/tests.yml << 'EOF'
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - run: pip install -r requirements.txt -r requirements-dev.txt
    - run: black --check src tests
    - run: flake8 src tests
    - run: mypy src --ignore-missing-imports
    - run: bandit -r src
    - run: pytest tests --cov=src
EOF

# Create Makefile
cat > Makefile << 'EOF'
.PHONY: help test lint format security clean

help:
	@echo "make test - Run tests"
	@echo "make lint - Run linters"
	@echo "make format - Format code"
	@echo "make security - Security scan"

test:
	pytest tests --cov=src

lint:
	black --check src tests
	flake8 src tests
	mypy src --ignore-missing-imports

format:
	black src tests

security:
	bandit -r src
	safety check

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov
EOF

git add .github/workflows/tests.yml Makefile
git commit -m "CI: Add GitHub Actions and Makefile"
```

---

## WEEK 2: TESTING & SECURITY (Days 6-12)

### Day 6-7: Unit Tests for Stage 1 (4 hours)

```bash
# Create comprehensive test file
cat > tests/test_stage_1.py << 'EOF'
import pytest
from pathlib import Path
from src.stage_1_quality_assurance import identify_files

@pytest.mark.unit
class TestIdentifyFiles:
    def test_finds_markdown_files(self, temp_dir, sample_markdown):
        """Test that markdown files are found."""
        files = identify_files(temp_dir)
        assert len(files) > 0
        assert all(f.suffix == ".md" for f in files)
    
    def test_ignores_non_markdown(self, temp_dir):
        """Test that non-markdown files are ignored."""
        (temp_dir / "readme.txt").write_text("test")
        files = identify_files(temp_dir)
        assert all(f.suffix == ".md" for f in files)
    
    def test_empty_directory(self, temp_dir):
        """Test handling of empty directory."""
        empty = temp_dir / "empty"
        empty.mkdir()
        files = identify_files(empty)
        assert len(files) == 0
    
    def test_nonexistent_path(self):
        """Test error handling for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            identify_files(Path("/nonexistent/path"))

# Run: pytest tests/test_stage_1.py -v
EOF

pytest tests/test_stage_1.py -v
```

### Day 8-9: Unit Tests for Remaining Stages (6 hours)

```bash
# Create test files for each stage
touch tests/test_stage_2.py tests/test_stage_3.py tests/test_stage_4.py tests/test_stage_5.py

# Each follows same pattern:
# 1. Test core functionality
# 2. Test error conditions
# 3. Test edge cases
# 4. Run: pytest tests/ -v --cov=src
```

### Day 10: Integration Tests (3 hours)

```bash
cat > tests/test_integration.py << 'EOF'
import pytest
from pathlib import Path
from src.orchestrate_import import ImportOrchestrator

@pytest.mark.integration
def test_full_pipeline(temp_dir):
    """Test complete 5-stage pipeline."""
    # Create sample files
    for i in range(5):
        (temp_dir / f"test_{i}.md").write_text(f"# File {i}\nContent")
    
    # Run pipeline
    orchestrator = ImportOrchestrator(
        source_dir=temp_dir,
        source_type="test",
        batch_id="integration-test",
        output_dir=temp_dir / "output"
    )
    result = orchestrator.run()
    
    # Verify success
    assert result.success
    assert result.files_processed == 5
    assert (temp_dir / "output").exists()

# Run: pytest tests/test_integration.py -v
EOF

pytest tests/test_integration.py -v
```

### Day 11: Input Validation & Error Handling (3 hours)

```bash
cat > tests/test_validation.py << 'EOF'
import pytest
from src.stage_1_quality_assurance import identify_files

@pytest.mark.unit
class TestInputValidation:
    def test_huge_file_rejected(self, temp_dir):
        """Test handling of oversized files."""
        huge = temp_dir / "huge.md"
        huge.write_text("x" * 10_000_000)  # 10MB
        
        files = identify_files(temp_dir, max_size=5_000_000)
        assert len(files) == 0
    
    def test_special_characters_handled(self, temp_dir):
        """Test handling of special characters."""
        special = temp_dir / "файл🚀test.md"
        special.write_text("# Test")
        
        files = identify_files(temp_dir)
        assert len(files) == 1
    
    def test_permission_error_handling(self, temp_dir):
        """Test handling of permission errors."""
        restricted = temp_dir / "restricted"
        restricted.mkdir()
        restricted.chmod(0o000)
        
        try:
            with pytest.raises(PermissionError):
                identify_files(restricted)
        finally:
            restricted.chmod(0o755)

# Run: pytest tests/test_validation.py -v
EOF

pytest tests/test_validation.py -v
```

### Day 12: Coverage & Reporting (2 hours)

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# Update requirements
cat > requirements-dev.txt << 'EOF'
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
EOF

git add tests/ requirements-dev.txt
git commit -m "Tests: Add comprehensive unit, integration, and validation tests (80%+ coverage)"
```

---

## WEEK 3: DOCUMENTATION & RELEASE (Days 13-21)

### Day 13-14: Documentation (4 hours)

```bash
# Create SECURITY.md
cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting Vulnerabilities

Email: security@yourproject.dev

Please include:
- Description of vulnerability
- Affected versions
- Steps to reproduce
- Suggested fix (if available)

## Scanning

All code is scanned with:
- Bandit (security linting)
- Safety (dependency vulnerabilities)
- MyPy (type checking)

## Supported Versions

| Version | Until |
|---------|-------|
| 1.0.x | 2026-12-31 |
| 0.x.x | 2025-12-31 |
EOF

# Create CONTRIBUTING.md
cat > CONTRIBUTING.md << 'EOF'
# Contributing Guidelines

## Requirements for Pull Requests

1. Tests pass: `pytest tests/`
2. Coverage > 85%: `pytest --cov=src`
3. No security issues: `bandit -r src/`
4. Clean linting: `black src/ && flake8 src/`
5. Types check: `mypy src/`
6. Updated CHANGELOG.md

## Workflow

1. Fork and create feature branch
2. Make changes with tests
3. Run: `make lint test security`
4. Update CHANGELOG.md
5. Push and open PR

## Code Review

All PRs require:
- Tests (85%+ coverage)
- Security scan clean
- Type checking passes
- 2 approvals
EOF

git add SECURITY.md CONTRIBUTING.md
git commit -m "Docs: Add security and contributing guidelines"
```

### Day 15: Release Preparation (2 hours)

```bash
# Update version
echo '__version__ = "0.1.0-alpha"' > src/__init__.py

# Create CHANGELOG.md
cat > CHANGELOG.md << 'EOF'
# Changelog

## [0.1.0-alpha] - 2025-01-15

### Added
- 5-stage batch import pipeline
- Stage 1: Quality assurance (linting, spell check)
- Stage 2: Layer 1 metadata generation
- Stage 3: Layer 2 semantic tagging
- Stage 4: Layer 3 placeholder generation
- Stage 5: Comprehensive validation
- Security scanning with Bandit
- Unit + integration tests (85%+ coverage)
- GitHub Actions CI/CD

### Security
- No hardcoded credentials
- Input validation on all paths
- Path traversal protection
- Sanitization of user input

### Known Issues
- Performance on files > 2MB (being optimized)
- Windows path handling needs testing
EOF

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="batch-import-system",
    version="0.1.0-alpha",
    description="Batch import for Logseq with security & testing",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/batch-import-system",
    license="MIT",
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
)
EOF

git add src/__init__.py CHANGELOG.md setup.py
git commit -m "Release: v0.1.0-alpha - Production ready"
```

### Day 16-17: GitHub Repository (2 hours)

```bash
# Push to GitHub (assuming remote is set up)
git remote add origin https://github.com/yourusername/batch-import-system.git
git branch -M main
git push -u origin main

# Create GitHub release
# (On GitHub.com)
# 1. Go to Releases → Create new release
# 2. Tag: v0.1.0-alpha
# 3. Title: "Initial Release - Production Ready"
# 4. Description: Use CHANGELOG.md content

# Verify GitHub Actions runs
# Should show all tests passing
```

### Day 18-21: Monitoring & Optimization (4 hours)

```bash
# Monitor test runs
# - Check GitHub Actions dashboard
# - Verify all Python versions pass
# - Verify all OS pass

# Performance optimization
# - Review coverage gaps
# - Add missing tests
# - Optimize slow operations

# Community setup
# - Star the repo
# - Add to personal website
# - Share with community
```

---

## AUTOMATION SCRIPTS

### Make Everything Run With One Command

```bash
# Create master script
cat > run-all-checks.sh << 'EOF'
#!/bin/bash
set -e

echo "🧹 Formatting code..."
black src tests

echo "✅ Linting..."
flake8 src tests
pylint src --exit-zero

echo "🔒 Security scan..."
bandit -r src
safety check

echo "📝 Type checking..."
mypy src --ignore-missing-imports

echo "🧪 Running tests..."
pytest tests --cov=src --cov-report=term-missing

echo "✨ All checks passed!"
EOF

chmod +x run-all-checks.sh

# Run with: ./run-all-checks.sh
```

---

## VERIFICATION CHECKLIST

Before considering code "production ready":

### Security
- [ ] Bandit report shows no CRITICAL/HIGH
- [ ] `safety check` passes
- [ ] No hardcoded secrets in code
- [ ] All inputs validated
- [ ] SECURITY.md published

### Testing
- [ ] Coverage > 85%
- [ ] All tests pass locally
- [ ] All tests pass in GitHub Actions
- [ ] Integration tests pass
- [ ] Edge cases handled

### Code Quality
- [ ] Black formatted
- [ ] Flake8 clean
- [ ] Pylint > 8.0
- [ ] MyPy passes
- [ ] No TODO/FIXME comments

### Documentation
- [ ] README complete
- [ ] CONTRIBUTING.md present
- [ ] SECURITY.md present
- [ ] CHANGELOG.md present
- [ ] Docstrings on all public functions

### Release Ready
- [ ] Version bumped
- [ ] LICENSE file present
- [ ] GitHub repository public
- [ ] GitHub Actions green
- [ ] Setup.py working

---

## QUICK STATUS CHECK

Run this to see if you're ready:

```bash
#!/bin/bash
echo "=== Status Check ==="

echo -n "✓ Git: "
git status > /dev/null 2>&1 && echo "OK" || echo "MISSING"

echo -n "✓ Tests: "
pytest tests/ -q > /dev/null 2>&1 && echo "OK (PASS)" || echo "FAIL"

echo -n "✓ Coverage: "
pytest --cov=src tests/ -q 2>/dev/null | grep -i "covered" && echo "OK" || echo "CHECK"

echo -n "✓ Security: "
bandit -q -r src/ > /dev/null 2>&1 && echo "OK" || echo "WARNINGS"

echo -n "✓ Linting: "
flake8 src --count 2>/dev/null | grep -q "0" && echo "OK" || echo "ISSUES"

echo "=== Done ==="
```

---

## TIMELINE SUMMARY

| Week | Focus | Deliverable |
|------|-------|------------|
| 1 | Foundation | Git, structure, basic CI/CD |
| 2 | Testing | 85%+ coverage, integration tests |
| 3 | Release | Docs, version, public ready |

**Total Time**: ~40-50 hours (can be spread over 3 weeks)  
**After Setup**: Each commit has automated quality checks  
**Maintenance**: ~5 hours/month for monitoring & updates

---

## NEXT STEPS

1. **Start Today**: Complete Day 1-2 (4 hours)
   - Get git + structure running
   - See green GitHub Actions
   
2. **This Week**: Complete Days 3-5 (6 hours)
   - First tests passing
   - Basic CI/CD working

3. **Next Week**: Complete Days 6-12 (20 hours)
   - 85%+ coverage
   - Production quality

4. **Third Week**: Complete Days 13-21 (10 hours)
   - Released to GitHub
   - Public ready

---

**Total Investment**: ~40 hours to go from "generated code" to "production-ready FOSS project"

**ROI**: Reusable for any future Python projects + industry-standard practices + ready for sharing/extension

**Questions?** Refer back to [SECURITY-TESTING-INFRASTRUCTURE.md](SECURITY-TESTING-INFRASTRUCTURE.md) for detailed explanations.

Start with Day 1 now! 🚀
