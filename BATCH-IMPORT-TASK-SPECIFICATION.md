# Batch Import Task Specification for LLM Agents

**Purpose**: Define the complete, reusable workflow for importing notes into three-layer Logseq system. This document enables any LLM agent to autonomously execute import batches with consistent quality and structure.

**System**: Multi-agent capable, programmatic, idempotent, reusable for any future note sources

---

## AGENT TASK STRUCTURE

### Overview Process
```
[INPUT: Raw Note Files]
    ↓
[STAGE 1: Markdown Quality Assurance]  (Task 1.1-1.4)
    ↓
[STAGE 2: Metadata Extraction & Layer 1 Population]  (Task 2.1-2.3)
    ↓
[STAGE 3: Semantic Tagging & Layer 2 Population]  (Task 3.1-3.3)
    ↓
[STAGE 4: Layer 3 Placeholder Generation]  (Task 4.1-4.3)
    ↓
[STAGE 5: Validation & Quality Checks]  (Task 5.1-5.4)
    ↓
[OUTPUT: Production-Ready Layered Notes]
```

Each stage produces intermediate artifacts that feed the next stage. All stages are scriptable and reusable.

---

## STAGE 1: MARKDOWN QUALITY ASSURANCE (30-45 min per 100 files)

**Purpose**: Ensure all markdown is clean, linted, and standardized before processing

**Documentation Reference**: 
- Read: `QUICK-REFERENCE-THREE-LAYER.md` → Tag Dimensions section
- Reference: `markdown-linting-rules.json` (generated in this stage)

### Task 1.1: Identify All Source Files
**Input**: Directory path (e.g., `/logseq_notes/`)  
**Process**:
- [ ] Recursively find all `.md` files
- [ ] Count total files
- [ ] Generate manifest: `import-manifest.csv` with columns:
  - `source_file`: Original path
  - `file_size_kb`: Size for batching
  - `estimated_layer1_difficulty`: auto (from Lighthouse structure) or manual
  - `estimated_tags`: Count of expected tags (auto)
  - `priority`: Order to process (smallest first for testing)

**Output**: `import-manifest.csv` with all files sorted by priority

**Script**: `scripts/1_1_identify_files.py`
```python
def identify_files(source_dir):
    """Generate comprehensive file manifest for import"""
    # Find all .md files
    # Extract metadata (size, path, source)
    # Sort by priority
    # Output manifest.csv
```

---

### Task 1.2: Lint Markdown Formatting
**Input**: All files from Task 1.1  
**Process**:
- [ ] For each file, run markdownlint checks:
  - [ ] Heading hierarchy valid (no skips: H1→H2→H3)
  - [ ] Consistent list formatting (- or * or +, not mixed)
  - [ ] Code blocks properly fenced (```language not ```)
  - [ ] Trailing spaces removed
  - [ ] Extra blank lines removed (max 1 between sections)
  - [ ] Bold/italic formatting consistent (**bold** not __bold__)
  - [ ] Links formatted correctly ([text](url))
  - [ ] No orphaned punctuation

**Issues to Track**:
- [ ] Log all linting issues to `linting-errors.log`
- [ ] Auto-fix common issues (trailing spaces, inconsistent lists, extra blanks)
- [ ] Flag complex issues for manual review: `linting-review-required.csv`

**Output**: 
- Clean markdown files (fixed in place)
- `linting-errors.log` (for review)
- `linting-review-required.csv` (manual queue)

**Script**: `scripts/1_2_lint_markdown.py`
```python
def lint_markdown(file_path):
    """Apply markdownlint rules, auto-fix what possible"""
    # Check all rules
    # Auto-fix safe issues
    # Return issues list and fixed content
```

---

### Task 1.3: Normalize Spelling & Grammar
**Input**: Linted markdown files  
**Process**:
- [ ] For each file, identify:
  - [ ] Spelling errors (using pyspellchecker against English dictionary + custom terms)
  - [ ] Common typos (using regex patterns from `typo-patterns.json`)
  - [ ] Grammar issues (capital letters after periods, etc.)
  - [ ] Consistency: "it's" vs "its", "affect" vs "effect", etc.

**Custom Dictionary** (don't flag as errors):
- Include course names: `Lighthouse Labs`, `VirtualBox`, `Cybersecurity`
- Include technical terms: `hypervisor`, `virtualization`, `firewalls`
- Load from: `custom-dictionary.json`

**Auto-fix**:
- Fix obvious typos from `typo-patterns.json`
- Flag others for manual review

**Output**:
- Clean content files
- `spelling-issues.csv` (for manual review)
- `grammar-issues.csv` (for manual review)

**Script**: `scripts/1_3_normalize_spelling.py`
```python
def normalize_spelling(file_content, custom_dict):
    """Identify and flag spelling/grammar issues"""
    # Check spelling against dictionary
    # Check grammar patterns
    # Return issues and suggestions
```

---

### Task 1.4: Extract & Clean Existing Metadata
**Input**: Cleaned markdown files  
**Process**:
- [ ] For each file, detect existing metadata:
  - [ ] YAML frontmatter (if present)
  - [ ] Properties blocks (if present)
  - [ ] Inline metadata comments (if present)
  - [ ] Existing tags (capture, will normalize in Stage 3)

**Clean**:
- [ ] Remove old/obsolete metadata
- [ ] Preserve creation dates
- [ ] Preserve file titles
- [ ] Remove duplicate tags (normalize in Stage 3)

**Output**:
- Cleaned files with minimal metadata
- `existing-metadata.csv` with extracted:
  - `file_name`
  - `existing_title`
  - `created_date` (if found)
  - `existing_tags` (as list)
  - `metadata_format` (YAML, Properties, Inline, None)

**Script**: `scripts/1_4_extract_metadata.py`
```python
def extract_existing_metadata(file_content):
    """Extract and clean existing metadata from file"""
    # Detect metadata format
    # Extract relevant fields
    # Clean and normalize
    # Return extracted data and clean content
```

**Output of Stage 1**: 
- All files lint-clean
- `import-manifest.csv` with all files
- `existing-metadata.csv` with extracted metadata
- `linting-review-required.csv` for manual fixes
- `spelling-issues.csv` for manual review
- Ready to proceed to Stage 2

---

## STAGE 2: METADATA EXTRACTION & LAYER 1 POPULATION (20-30 min per 100 files)

**Purpose**: Apply Layer 1 structure (hierarchy + chronological + source tracking)

**Documentation Reference**:
- Read: `THREE-LAYER-LOGSEQ-ARCHITECTURE.md` → Layer 1 specification
- Reference: `import-manifest.csv` from Stage 1
- Reference: `existing-metadata.csv` from Stage 1

### Task 2.1: Map File to Source Hierarchy
**Input**: 
- File paths from manifest
- Source directory structure (e.g., Lighthouse Labs: `Course_N/Week_N/Topic.md`)

**Process**:
- [ ] Parse file path to extract hierarchy
- [ ] Detect source type:
  - [ ] Lighthouse Labs: Extract Course X, Week Y, Topic Z
  - [ ] Perplexity: Extract chat/topic/date
  - [ ] VS Code: Extract project/file path
  - [ ] Journal: Extract date/category
  - [ ] Other: Use directory structure

**Build Hierarchy Data**:
```csv
file_name,source_type,hierarchy_level_1,hierarchy_level_2,hierarchy_level_3,hierarchy_level_4,sort_key
2024_04_01.md,journal,2024,April,01,,,2024-04-01
Week_1_Virtualization.md,lighthouse_labs,Course_1,Week_1,Virtualization,,course-1-week-1-virtualization
```

**Output**: `hierarchy-mapping.csv`

**Script**: `scripts/2_1_map_hierarchy.py`
```python
def map_file_to_hierarchy(file_path, source_type_map):
    """Extract hierarchy from file path/structure"""
    # Detect source type
    # Parse path structure
    # Extract hierarchy levels
    # Return hierarchy dict
```

---

### Task 2.2: Build Layer 1 Frontmatter
**Input**: 
- Hierarchy mapping from Task 2.1
- Existing metadata from Stage 1

**Process**:
For each file, create Layer 1 frontmatter:
```markdown
---
source: lighthouse-labs
source-file-original: Course_1/Week_1/Virtualization.md
hierarchy:
  - course: 1
  - week: 1
  - topic: Virtualization
hierarchy-full: "[[Course 1 - IT Essentials]] > [[Week 1]] > [[Virtualization]]"
created-date: 2025-01-15
created-chronological: 2025-W03
last-modified: 2025-12-18
import-date: 2025-12-18
import-batch: "lighthouse-labs-batch-1"
status: imported
---
```

**Rules**:
- [ ] Every file gets all Layer 1 fields (even if empty)
- [ ] Dates in ISO format: YYYY-MM-DD
- [ ] Chronological in: YYYY-WXX format
- [ ] Link hierarchy back to index pages (will validate in Stage 5)
- [ ] Import batch ID for tracking

**Output**: 
- All files have Layer 1 frontmatter added
- `layer1-applied.csv` tracking which files got which hierarchy

**Script**: `scripts/2_2_build_layer1.py`
```python
def build_layer1_frontmatter(hierarchy_data, existing_metadata):
    """Create Layer 1 frontmatter block"""
    # Build YAML frontmatter
    # Ensure all required fields present
    # Create hierarchy links
    # Return frontmatter string
```

---

### Task 2.3: Validate Layer 1 Integrity
**Input**: Files with Layer 1 frontmatter  
**Process**:
- [ ] For each file, check:
  - [ ] YAML frontmatter parses correctly
  - [ ] All required fields present (source, hierarchy, created-date, import-date, status)
  - [ ] Date formats valid (ISO YYYY-MM-DD and chronological YYYY-WXX)
  - [ ] Hierarchy levels make sense (no Course > Month jumps)
  - [ ] Import batch ID matches expected batch

**Issues**:
- [ ] Log validation failures to `layer1-validation-failures.csv`
- [ ] Auto-fix obvious date format issues
- [ ] Flag content mismatches for manual review

**Output**: 
- All files pass Layer 1 validation
- `layer1-validation-results.csv` with pass/fail/fixed for each file

**Script**: `scripts/2_3_validate_layer1.py`
```python
def validate_layer1(frontmatter_dict):
    """Validate Layer 1 structure and content"""
    # Check all required fields
    # Validate date formats
    # Check hierarchy consistency
    # Return validation result and issues
```

**Output of Stage 2**:
- All files have proper Layer 1 structure
- `layer1-applied.csv` with hierarchy mapping
- `layer1-validation-results.csv` with validation status
- Ready to proceed to Stage 3

---

## STAGE 3: SEMANTIC TAGGING & LAYER 2 POPULATION (30-45 min per 100 files)

**Purpose**: Apply Layer 2 multi-dimensional tags for proficiency, domain, activity, project, goal, connections, readiness, source

**Documentation Reference**:
- Read: `THREE-LAYER-LOGSEQ-ARCHITECTURE.md` → Layer 2 Tag Dimensions
- Read: `QUICK-REFERENCE-THREE-LAYER.md` → Tag Dimensions table
- Reference: `tag-schema.json` (master tag definitions)
- Reference: `tag-mapping-lighthouse-labs.csv` (course→tags mapping)

### Task 3.1: Extract Content Keywords for Auto-Tagging
**Input**: File content from files  
**Process**:
- [ ] For each file, extract:
  - [ ] Title (primary descriptor)
  - [ ] First paragraph (context)
  - [ ] All headings (topic structure)
  - [ ] Technical terms (from technical-terms.json)
  - [ ] Concepts mentioned

**Keyword Extraction**:
- [ ] Use NLP to identify 5-10 key concepts per file
- [ ] Cross-reference against `domain-terms-database.json`
- [ ] Match file type (if Lighthouse Labs, use course-week-topic)

**Output**: `content-keywords.csv` with:
- `file_name`
- `extracted_keywords` (list)
- `extracted_domain` (best match from domain list)
- `extracted_topics` (2-5 main topics)
- `confidence` (how confident we are)

**Script**: `scripts/3_1_extract_keywords.py`
```python
def extract_keywords(file_content, domain_db, tech_terms_db):
    """Extract keywords and infer domain from content"""
    # Parse content
    # Find technical terms
    # Infer domain
    # Extract key concepts
    # Return keywords and metadata
```

---

### Task 3.2: Map Keywords to Tags
**Input**: 
- Keywords from Task 3.1
- Tag schema from `tag-schema.json`
- Source-specific mappings (e.g., `tag-mapping-lighthouse-labs.csv`)

**Process**:
Build tags across all 8 dimensions:

1. **Domain Tags** (from `tag-mapping-{source}.csv`):
   - Input: Course/Week/Topic from hierarchy
   - Output: `#domain/cybersecurity/network-security` (hierarchical)
   - Rules: 2-4 levels deep, max 1 primary domain per file

2. **Activity Tags** (inferred from content):
   - Analyze if file is: learning material, practical exercise, reference, project setup, etc.
   - Output: `#activity/learn::beginner` or `#activity/execute::hands-on`
   - Rules: 1-2 activity tags per file

3. **Proficiency Tags** (initialized):
   - New import = `#proficiency/topic::beginner` (user will update)
   - Output: `#proficiency/{topic-name}::beginner`
   - Rules: 1 per file initially, updated by user over time

4. **Project Tags** (if applicable):
   - Match file to known projects (from `projects-list.json`)
   - Output: `#project/{project-name}` (if applicable)
   - Rules: Optional, 0-2 per file

5. **Goal Tags** (if applicable):
   - Match to user's goals (from `goals-list.json`)
   - Output: `#goal/{goal-type}/{goal-name}`
   - Rules: Optional, 0-2 per file

6. **Connection Tags** (placeholders):
   - Output: `#prerequisite-for/`, `#enables/`, `#connects-to/` (empty for Layer 3)
   - Rules: Populated in Stage 4

7. **Readiness Tags** (if applicable):
   - Output: `#readiness/{role}::...` (if file demonstrates job readiness)
   - Rules: Optional, 0-1 per file

8. **Source Tags** (from source type):
   - Output: `#source/lighthouse-labs` or `#source/perplexity` etc.
   - Rules: Always 1, plus `#quality/verified` if applicable

**Output**: `tags-applied.csv` with:
- `file_name`
- `domain_tags`
- `activity_tags`
- `proficiency_tags`
- `project_tags`
- `goal_tags`
- `connection_tags`
- `readiness_tags`
- `source_tags`
- `confidence` (for auto-generated tags)

**Script**: `scripts/3_2_map_to_tags.py`
```python
def map_keywords_to_tags(keywords, domain_db, tag_schema, source_mappings):
    """Convert keywords to multi-dimensional tags"""
    # For each dimension, find matching tags
    # Apply hierarchy and rules
    # Return tag dict for all 8 dimensions
```

---

### Task 3.3: Apply Tags to Files & Validate
**Input**: 
- Files with Layer 1
- Tags from Task 3.2

**Process**:
- [ ] For each file, create "Tags" section after Layer 1 frontmatter:
```markdown
---
[Layer 1 Frontmatter]
---

## Tags

#source/lighthouse-labs #quality/verified
#domain/cybersecurity/network-security/firewalls
#activity/learn::intermediate
#proficiency/firewalls-fundamentals::beginner
```

**Validation**:
- [ ] All tags follow format: `#dimension/path/path::level` (or just `#dimension/path`)
- [ ] No duplicate tags
- [ ] No invalid dimensions
- [ ] Proficiency level is valid (novice, beginner, intermediate, competent, expert, gap, strength)
- [ ] Domain hierarchy is consistent

**Issues**:
- [ ] Log validation failures to `tags-validation-failures.csv`
- [ ] Flag low-confidence auto-generated tags for manual review

**Output**: 
- All files have Layer 2 tags applied
- `tags-applied.csv` with all tags for each file
- `tags-validation-failures.csv` for manual review

**Script**: `scripts/3_3_validate_tags.py`
```python
def validate_tags(tags_dict, tag_schema):
    """Validate Layer 2 tags against schema"""
    # Check format
    # Validate dimensions
    # Check proficiency levels
    # Return validation result
```

**Output of Stage 3**:
- All files have Layer 2 tags properly applied
- `tags-applied.csv` with all tag mappings
- `tags-validation-failures.csv` for manual fixes
- Ready to proceed to Stage 4

---

## STAGE 4: LAYER 3 PLACEHOLDER GENERATION (20-30 min per 100 files)

**Purpose**: Create Layer 3 connection placeholders (prerequisites, enables, project links, goal links)

**Documentation Reference**:
- Read: `THREE-LAYER-LOGSEQ-ARCHITECTURE.md` → Layer 3 Linking Protocol
- Reference: `graph-structure-map.json` (known connections)

### Task 4.1: Detect Potential Layer 3 Connections
**Input**: 
- File content
- Tags from Stage 3
- Existing graph structure (if any)

**Process**:
- [ ] For each file, analyze content to identify:
  - [ ] Prerequisites mentioned in text (e.g., "requires knowledge of X")
  - [ ] Concepts this enables (e.g., "builds on this foundation")
  - [ ] Related topics (from content similarity)
  - [ ] Project applicability (from tags and content)
  - [ ] Goal relevance (from tags)

**Detection Methods**:
1. **Keyword matching**: Look for "prerequisite", "requires", "builds on", "enables", "next step"
2. **Content similarity**: Compare with existing page titles in graph
3. **Tag inference**: If tagged with `#project/homelab`, likely connects to homelab project
4. **Domain analysis**: Files in same domain likely connected

**Output**: `layer3-candidates.csv` with:
- `file_name`
- `potential_prerequisites` (list of likely files)
- `potential_enables` (list of likely files)
- `potential_project_connections` (list of projects)
- `potential_goal_connections` (list of goals)
- `confidence` (high/medium/low)

**Script**: `scripts/4_1_detect_connections.py`
```python
def detect_layer3_connections(file_content, tags, graph_structure):
    """Identify potential Layer 3 connections"""
    # Look for prerequisite/enable keywords
    # Match content similarity
    # Check tag-based connections
    # Return candidates with confidence
```

---

### Task 4.2: Build Layer 3 Placeholder Sections
**Input**: 
- Files with Layers 1-2
- Connection candidates from Task 4.1

**Process**:
Create placeholder sections for Layer 3 (to be manually populated):

```markdown
---
[Layer 1 Frontmatter]
---

## Tags
[Layer 2 Tags]

## Prerequisites
- [ ] [[]]  # User will populate
- [ ] [[]]

## Enables
- [ ] [[]]  # User will populate
- [ ] [[]]

## Project Connections
- [ ] [[]]  # User will populate

## Goal Connections
- [ ] [[]]  # User will populate

## See Also
- Connection candidates (with confidence):
  - `medium-confidence`: [[File A]], [[File B]]
  - `low-confidence`: [[File C]]

[Original Content Below]
```

**Rules**:
- [ ] Empty checkboxes for user to fill in
- [ ] Candidates listed for guidance (not auto-populated)
- [ ] Clear marker where original content begins

**Output**: Files with Layer 3 placeholder sections

**Script**: `scripts/4_2_build_layer3_placeholders.py`
```python
def build_layer3_placeholders(connection_candidates, confidence_threshold):
    """Create Layer 3 placeholder sections"""
    # Build prerequisite/enables lists
    # Build project/goal connection sections
    # Add candidates for guidance
    # Return placeholder text
```

---

### Task 4.3: Validate Layer 3 Structure
**Input**: Files with Layer 3 placeholders  
**Process**:
- [ ] For each file, verify:
  - [ ] Placeholder sections present
  - [ ] Placeholder format correct (checkboxes, links)
  - [ ] Original content is intact and follows placeholders

**Output**: `layer3-structure-validation.csv`

**Script**: `scripts/4_3_validate_layer3.py`
```python
def validate_layer3_structure(file_content):
    """Validate Layer 3 placeholder structure"""
    # Check sections present
    # Validate format
    # Ensure content intact
    # Return validation result
```

**Output of Stage 4**:
- All files have Layer 3 placeholder sections created
- `layer3-candidates.csv` with connection suggestions
- `layer3-structure-validation.csv` with validation status
- Ready to proceed to Stage 5

---

## STAGE 5: VALIDATION & QUALITY CHECKS (15-20 min per 100 files)

**Purpose**: Comprehensive QA before production deployment

**Documentation Reference**:
- Read: `QUICK-REFERENCE-THREE-LAYER.md` → What Success Looks Like

### Task 5.1: Full File Integrity Validation
**Input**: Files from all 4 stages  
**Process**:
- [ ] For each file, verify:
  - [ ] File readable and parses as valid markdown
  - [ ] Layer 1 frontmatter valid YAML
  - [ ] Layer 2 tags all valid
  - [ ] Layer 3 structure intact
  - [ ] Original content preserved
  - [ ] No duplicate content blocks
  - [ ] File size reasonable (< 5MB)
  - [ ] Character encoding UTF-8

**Output**: `integrity-validation.csv` with pass/fail for each check

**Script**: `scripts/5_1_validate_integrity.py`
```python
def validate_file_integrity(file_content, file_path):
    """Comprehensive file integrity check"""
    # Check all criteria
    # Return detailed validation result
```

---

### Task 5.2: Cross-File Consistency Check
**Input**: All files from batch  
**Process**:
- [ ] Check across all files:
  - [ ] No duplicate file names
  - [ ] Hierarchy levels are consistent (no stray files)
  - [ ] Import batch IDs all match expected
  - [ ] Date ranges make sense (chronological tags in order)
  - [ ] Tags used consistently (no typos in tag names)
  - [ ] Source types all recognized

**Output**: `consistency-validation.csv` with batch-level checks

**Script**: `scripts/5_2_validate_consistency.py`
```python
def validate_batch_consistency(all_files_metadata):
    """Check consistency across entire batch"""
    # Check for duplicates
    # Validate hierarchy
    # Check tag consistency
    # Return batch validation result
```

---

### Task 5.3: Tag Coverage Analysis
**Input**: All files with tags  
**Process**:
Generate statistics:
- [ ] Distribution of domain tags (how many per domain)
- [ ] Distribution of activity tags
- [ ] Distribution of proficiency levels (should be mostly beginner on import)
- [ ] Coverage of source tags (should be 100%)
- [ ] Coverage of connection placeholders (should be 100%)

**Anomalies to Flag**:
- [ ] Files with no tags (should have at least source tag)
- [ ] Files with > 10 tags (probably over-tagged)
- [ ] Proficiency tags not all at beginner (check before import)

**Output**: `tag-coverage-analysis.csv` and `tag-anomalies.csv`

**Script**: `scripts/5_3_analyze_tag_coverage.py`
```python
def analyze_tag_coverage(all_files_metadata):
    """Generate tag coverage statistics and identify anomalies"""
    # Count tags by dimension
    # Find anomalies
    # Return statistics
```

---

### Task 5.4: Generate Final Import Report
**Input**: 
- All validation results from 5.1-5.3
- All stage outputs (manifest, hierarchy, tags, candidates)

**Process**:
Create comprehensive import report:

```markdown
# Import Batch Report

**Batch ID**: lighthouse-labs-batch-1
**Import Date**: 2025-12-18
**Total Files**: 600
**Status**: READY FOR DEPLOYMENT

## Summary
- ✅ All 600 files processed
- ✅ 100% Layer 1 integrity
- ✅ 99.5% Layer 2 tag coverage
- ✅ 100% Layer 3 placeholders created
- ⚠️  3 files require manual tag review (see tag-anomalies.csv)
- ⚠️  2 files have spelling issues (see spelling-issues.csv)

## Processing Summary
- Markdown Quality: 598/600 passed, 2 manual review
- Layer 1 Applied: 600/600 (100%)
- Layer 2 Tags Applied: 600/600 (100%)
- Layer 3 Placeholders: 600/600 (100%)
- Validation Passed: 598/600 (99.7%)

## Statistics
- Average tags per file: 7.2
- Domain coverage: 12 domains, evenly distributed
- Activity types: 5 types identified
- Proficiency levels: 595 beginner, 5 intermediate (expected)
- Project connections found: 28 files
- Goal connections found: 15 files

## Files Requiring Manual Review
See: `linting-review-required.csv`, `spelling-issues.csv`, `tag-anomalies.csv`
Count: 3-5 files (< 1%)

## Deployment Next Steps
1. Back up existing Logseq graph: `cp -r ~/Logseq/graph ~/Logseq/graph.backup.2025-12-18`
2. Copy files: `cp processed-files/*.md ~/Logseq/graph/pages/`
3. Restart Logseq
4. Run: Settings → Advanced → Clear caches and re-index
5. Verify: Search for `#source/lighthouse-labs` returns 600 results

## Files Ready for Deployment
- `processed-batch-files/` directory contains all 600 files ready to import
- All files validated and ready for production
```

**Output**: `import-batch-report.md`

**Script**: `scripts/5_4_generate_report.py`
```python
def generate_import_report(all_validation_results, statistics):
    """Generate comprehensive import report"""
    # Compile all results
    # Generate statistics
    # Create deployment checklist
    # Return report markdown
```

**Output of Stage 5**:
- Comprehensive import report
- All validation results documented
- Batch ready for production deployment
- Clear next steps for deployment

---

## EXECUTION WORKFLOW FOR AGENTS

### High-Level Agent Flow
```
INPUT: task_spec.json containing:
  - source_directory
  - source_type (lighthouse_labs | perplexity | vs_code_notes | journals | other)
  - batch_id
  - output_directory

EXECUTE:
  1. Run Stage 1 (all tasks 1.1-1.4)
  2. Review flagged items: linting-review-required.csv, spelling-issues.csv
  3. If critical issues, STOP and report to human
  4. Run Stage 2 (all tasks 2.1-2.3)
  5. Review flagged items: layer1-validation-failures.csv
  6. If critical issues, STOP and report to human
  7. Run Stage 3 (all tasks 3.1-3.3)
  8. Review flagged items: tags-validation-failures.csv
  9. If critical issues, STOP and report to human
  10. Run Stage 4 (all tasks 4.1-4.3)
  11. Run Stage 5 (all tasks 5.1-5.4)
  12. Output: import-batch-report.md with deployment status

SUCCESS CRITERIA:
  - integrity-validation.csv: ALL files pass
  - consistency-validation.csv: ALL checks pass
  - tag-coverage-analysis.csv: no critical anomalies
  - < 2% files requiring manual review
  - import-batch-report.md status: READY FOR DEPLOYMENT

OUTPUT ARTIFACTS:
  - processed-batch-files/ directory with all processed markdown
  - import-batch-report.md with deployment instructions
  - All CSV files for tracking and manual review
  - All intermediate artifacts for debugging
```

### Running a Single Import Batch (Command Line)

```bash
# Define task specification
python3 scripts/orchestrate_import.py \
  --source-dir /path/to/source/files \
  --source-type lighthouse_labs \
  --batch-id lighthouse-labs-batch-1 \
  --output-dir /path/to/output \
  --config config.json

# This single command runs all 5 stages
```

---

## CONFIGURATION FILES REQUIRED

### `config.json`
```json
{
  "domain_mappings": {
    "lighthouse_labs": "tag-mapping-lighthouse-labs.csv"
  },
  "custom_dictionary": "custom-dictionary.json",
  "technical_terms_db": "technical-terms.json",
  "tag_schema": "tag-schema.json",
  "typo_patterns": "typo-patterns.json",
  "projects_list": "projects-list.json",
  "goals_list": "goals-list.json",
  "graph_structure": "graph-structure-map.json"
}
```

### Key Reference Files to Create
1. `tag-mapping-lighthouse-labs.csv` - Maps Course/Week/Topic to domain tags
2. `custom-dictionary.json` - Technical terms to exclude from spell check
3. `technical-terms.json` - Database of technical terms for keyword extraction
4. `tag-schema.json` - Master tag definitions and validation rules
5. `typo-patterns.json` - Common typos and corrections
6. `projects-list.json` - Known projects for matching
7. `goals-list.json` - User's goals for matching
8. `graph-structure-map.json` - Known connections in existing graph

---

## ERROR HANDLING & RECOVERY

### If Stage 1 Fails
- Review `linting-review-required.csv`
- Manually fix files in `manual-review/`
- Run Stage 1 again on fixed files
- Continue to Stage 2

### If Stage 2 Fails
- Review `layer1-validation-failures.csv`
- Check hierarchy mapping in `hierarchy-mapping.csv`
- Fix date format issues
- Re-run Stage 2 on affected files

### If Stage 3 Fails
- Review `tags-validation-failures.csv`
- Check tag schema in `tag-schema.json`
- Verify tag dimensions are valid
- Re-run Stage 3 on affected files

### If Stage 4 Fails
- Less critical (placeholders are guidance)
- Review `layer3-candidates.csv` anyway
- Ensure structure is valid

### If Stage 5 Fails
- DO NOT DEPLOY
- Fix all issues identified in validation CSVs
- Re-run Stage 5 on entire batch
- Only deploy when status is READY

---

## DEPLOYMENT CHECKLIST

Once `import-batch-report.md` shows status: READY FOR DEPLOYMENT

```
Pre-Deployment (5 min)
- [ ] Back up existing Logseq graph
- [ ] Verify output directory has all 600 files
- [ ] Copy import-batch-report.md to notes directory
- [ ] Save all CSV files to archive directory

Deployment (5 min)
- [ ] Copy all processed files to ~/Logseq/graph/pages/
- [ ] Restart Logseq
- [ ] Run: Settings → Advanced → Clear caches and re-index
- [ ] Wait for indexing (2-5 minutes)

Verification (10 min)
- [ ] Search: `#source/lighthouse-labs` → should return ~600 files
- [ ] Search: `#proficiency/::beginner` → should return ~595 files
- [ ] Navigate: `[[Course 1 - IT Essentials]]` → should work
- [ ] Query: Run one saved query from QUICK-REFERENCE → should work
- [ ] Tag check: Sample 5 random files, verify tags make sense

Post-Deployment (ongoing)
- [ ] User reviews Layer 3 candidates in "See Also" sections
- [ ] User populates prerequisites/enables as they study
- [ ] User updates proficiency tags over time
- [ ] Track metrics: files reviewed, tags updated, proficiency growth
```

---

## METRICS & TRACKING

### Per-Batch Metrics
- Files processed: count
- Processing time: total and per-file average
- Quality: % passing each validation
- Manual review count: files requiring human attention
- Error rate: files failing validation

### Cumulative Metrics
- Total files imported to date
- Total tags applied
- Tag dimensions used
- Average tags per file
- Quality trend: are recent batches higher quality?

### User Progress Metrics (after Layer 3 population)
- Files reviewed by user: count
- Proficiency tags updated: count
- Layer 3 connections populated: count
- Projects using knowledge: count
- Average proficiency level: trending over time

---

## REUSABILITY FOR FUTURE IMPORTS

This entire system is designed to be run repeatedly for:
- New course materials
- Perplexity research batches
- VS Code export batches
- Journal entries
- Any other markdown source

**To reuse**:
1. Create new batch_id
2. Create new source_type mapping (if needed)
3. Point to new source directory
4. Run: `python3 scripts/orchestrate_import.py --batch-id [new_batch_id] --source-type [type]`
5. All stages run automatically
6. Get deployment report

**Expected time**: 
- 100 files: ~3-4 hours (1st run with setup), ~1 hour (subsequent runs)
- 600 files: ~15-20 hours (1st run), ~8-10 hours (subsequent runs)
- Can be run in parallel on multiple batches

---

## SUCCESS CRITERIA FOR COMPLETE SYSTEM

After all 5 stages complete, you should be able to answer:

✅ **"Can I search for notes by domain?"**
- Run: `#domain/cybersecurity` → all cybersecurity notes appear

✅ **"Can I see my learning hierarchy?"**
- Navigate: `[[Course 1]]` → see all weeks → see all topics

✅ **"Do I know what's new?"**
- Search: `created-chronological: 2025-W50` → see this week's imports

✅ **"Can I track where notes came from?"**
- Check Layer 1 frontmatter → source, original file path, import date

✅ **"Are tags consistent and correct?"**
- Sample 20 random files → all tags valid and make sense

✅ **"Are placeholders ready for Layer 3?"**
- Sample 10 files → all have prerequisite/enables/project/goal sections

✅ **"Is the batch production-ready?"**
- `import-batch-report.md` status: READY FOR DEPLOYMENT

---

**This specification enables any agent to execute consistent, high-quality imports repeatedly and reliably.**

End of specification.
