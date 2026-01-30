# LLM Agent Task List: Automated Batch Import

**For**: Any LLM Agent executing batch imports autonomously  
**Purpose**: Execute the complete import pipeline with quality assurance and human oversight  
**Status**: Ready for autonomous execution

---

## OVERVIEW

**System**: Five-stage batch import pipeline with autonomous processing and quality checkpoints  
**Expected Duration**: 2-4 hours per 600 files  
**Success Criteria**: Deployment status "✅ READY FOR DEPLOYMENT" with < 1% anomalies

---

## PRE-EXECUTION CHECKLIST

### ✅ Verify Environment

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Required packages: `pip install pandas pyyaml spellchecker`
- [ ] Scripts directory exists with all 5 stage modules
- [ ] Configuration file present: `scripts/config.json`
- [ ] Reference files present in `scripts/dictionaries/`, `scripts/schemas/`

### ✅ Prepare Source Files

- [ ] Source directory identified
- [ ] Source type verified: `lighthouse_labs | perplexity | vs_code_notes | journals | other`
- [ ] Batch ID created: format `{source}-batch-{number}` (e.g., `lighthouse-labs-batch-1`)
- [ ] Output directory ready for processing
- [ ] Total file count known and logged

### ✅ Documentation Ready

- [ ] `BATCH-IMPORT-TASK-SPECIFICATION.md` available for reference
- [ ] `IMPORT-PIPELINE-SETUP.md` available for troubleshooting
- [ ] `THREE-LAYER-LOGSEQ-ARCHITECTURE.md` available for understanding structure
- [ ] `config.json` reviewed and customized if needed

---

## TASK 1: INITIALIZE ORCHESTRATOR

**Time**: 5 minutes  
**Document**: IMPORT-PIPELINE-SETUP.md → Quick Start  
**Autonomous**: Yes

```python
# Initialize the orchestrator
from pathlib import Path
from scripts.orchestrate_import import ImportOrchestrator

orchestrator = ImportOrchestrator(
    source_dir="/path/to/source/files",
    source_type="lighthouse_labs",  # or perplexity, vs_code_notes, journals, other
    batch_id="lighthouse-labs-batch-1",
    output_dir="/path/to/output",
    config_path="scripts/config.json"
)
```

**Checkpoint**: Orchestrator initialized without errors  
**On Failure**: Check paths and config file, review setup guide

---

## TASK 2: EXECUTE STAGE 1 - MARKDOWN QUALITY ASSURANCE

**Time**: 30-45 min per 100 files  
**Document**: BATCH-IMPORT-TASK-SPECIFICATION.md → Stage 1  
**Autonomous**: Yes

```python
success = orchestrator.run_stage_1_qa()
```

**This Stage Does**:

- ✅ Task 1.1: Identifies all .md files and creates manifest
- ✅ Task 1.2: Lints markdown for heading hierarchy, list consistency, code blocks, trailing spaces
- ✅ Task 1.3: Checks spelling/grammar, flags anomalies
- ✅ Task 1.4: Extracts existing metadata (YAML, properties, inline)

**Output Files Generated**:

- `import-manifest.csv` - All files with priority
- `linting-errors.csv` - Auto-fixable linting issues (fixed)
- `linting-review-required.csv` - Complex issues needing manual review
- `spelling-issues.csv` - Spelling and grammar findings
- `existing-metadata.csv` - Extracted metadata from files

**Checkpoint**: Check success flag

```python
if not success:
    logger.error("Stage 1 failed. Review:")
    print(open("import-orchestration.log").read()[-500:])
    # STOP - have human review linting-review-required.csv
    exit(1)
```

**Allowed To Continue If**:

- < 5% files in `linting-review-required.csv`
- No critical errors in log
- Manifest contains expected file count

---

## TASK 3: EXECUTE STAGE 2 - LAYER 1 METADATA POPULATION

**Time**: 20-30 min per 100 files  
**Document**: BATCH-IMPORT-TASK-SPECIFICATION.md → Stage 2  
**Autonomous**: Yes

```python
success = orchestrator.run_stage_2_layer1()
```

**This Stage Does**:

- ✅ Task 2.1: Parses file paths to extract hierarchy (course/week/topic)
- ✅ Task 2.2: Builds YAML frontmatter with source, hierarchy, dates, import info
- ✅ Task 2.3: Validates frontmatter structure and date formats

**Output Files Generated**:

- `hierarchy-mapping.csv` - Extracted hierarchy for each file
- `layer1-applied.csv` - Hierarchy mapping by file
- `layer1-validation-results.csv` - Validation pass/fail for each file

**Example Layer 1 Frontmatter Created**:

```yaml
---
source: lighthouse-labs
source-file-original: Course_1/Week_1/Virtualization.md
hierarchy:
  course: 1
  week: 1
  topic: Virtualization
hierarchy-full: "Course 1 > Week 1 > Virtualization"
created-date: 2025-01-15
created-chronological: 2025-W03
import-date: 2025-12-18
import-batch: lighthouse-labs-batch-1
status: imported
---
```

**Checkpoint**: Check success and validation results

```python
if not success:
    logger.error("Stage 2 failed")
    exit(1)

validation = orchestrator.stage_outputs.get('layer1_validation', {})
if validation.get('files_failed', 0) > 0:
    logger.warning(f"⚠️  {validation['files_failed']} files failed Layer 1 validation")
    # Review layer1-validation-results.csv for details
```

**Allowed To Continue If**:

- 100% of files have valid YAML frontmatter
- All required Layer 1 fields present
- Dates are valid ISO format and chronological

---

## TASK 4: EXECUTE STAGE 3 - SEMANTIC TAGGING & LAYER 2 POPULATION

**Time**: 30-45 min per 100 files  
**Document**: BATCH-IMPORT-TASK-SPECIFICATION.md → Stage 3  
**Document**: QUICK-REFERENCE-THREE-LAYER.md → Tag Dimensions  
**Autonomous**: Yes

```python
success = orchestrator.run_stage_3_layer2()
```

**This Stage Does**:

- ✅ Task 3.1: Extracts keywords from content (title, headings, technical terms)
- ✅ Task 3.2: Maps keywords to multi-dimensional tags (8 dimensions)
- ✅ Task 3.3: Validates tags and applies to files

**Tags Applied**:

1. **Domain**: `#domain/cybersecurity/network-security` (inferred from content)
2. **Activity**: `#activity/learn::beginner` (inferred from content type)
3. **Proficiency**: `#proficiency/topic::beginner` (default on import, user updates)
4. **Project**: Empty (user populates)
5. **Goal**: Empty (user populates)
6. **Connection**: Empty placeholders (Layer 3)
7. **Readiness**: Empty (user populates when ready)
8. **Source**: `#source/lighthouse-labs` (from source type)

**Output Files Generated**:

- `content-keywords.csv` - Extracted keywords per file
- `tags-mapped.csv` - All tags mapped per file
- `tags-validation-results.csv` - Validation pass/fail

**Example Tags Section Created**:

```markdown
## Tags

#source/lighthouse-labs #quality/verified
#domain/cybersecurity/network-security/firewalls
#activity/learn::intermediate
#proficiency/firewalls-fundamentals::beginner
```

**Checkpoint**: Check success and tag statistics

```python
if not success:
    logger.error("Stage 3 failed")
    exit(1)

# Check tag coverage
import pandas as pd
tag_results = pd.read_csv("output/stage_5_validation/tags-validation-results.csv")
pass_rate = (tag_results['status'] == 'PASS').sum() / len(tag_results)
logger.info(f"Tag pass rate: {pass_rate * 100:.1f}%")
```

**Allowed To Continue If**:

- 95%+ files have valid tags
- All source tags are present
- No anomalies in tag format

---

## TASK 5: EXECUTE STAGE 4 - LAYER 3 PLACEHOLDER GENERATION

**Time**: 20-30 min per 100 files  
**Document**: BATCH-IMPORT-TASK-SPECIFICATION.md → Stage 4  
**Autonomous**: Yes

```python
success = orchestrator.run_stage_4_layer3()
```

**This Stage Does**:

- ✅ Task 4.1: Analyzes content for connection keywords (prerequisite, enables, etc.)
- ✅ Task 4.2: Creates placeholder sections for user to populate during review
- ✅ Task 4.3: Validates placeholder structure

**Placeholders Created**:

```markdown
## Prerequisites
- [ ] [[]]  # User will populate
- [ ] [[]]

## Enables
- [ ] [[]]  # Concepts this enables
- [ ] [[]]

## Project Connections
- [ ] [[]]  # Applicable projects

## Goal Connections
- [ ] [[]]  # Supporting career goals

## See Also
Connection candidates:
- [suggestions with confidence levels]
```

**Output Files Generated**:

- `layer3-candidates.csv` - Suggested connections (guidance only)
- `layer3-structure-validation.csv` - Placeholder structure validation

**Checkpoint**: Check success

```python
if not success:
    logger.error("Stage 4 failed - placeholders not created")
    exit(1)

logger.info("✅ Layer 3 placeholders created - ready for user population")
```

**Allowed To Continue If**:

- 100% files have placeholder sections
- All required sections present
- Structure is valid for user to populate

---

## TASK 6: EXECUTE STAGE 5 - VALIDATION & QUALITY CHECKS

**Time**: 15-20 min per 100 files  
**Document**: BATCH-IMPORT-TASK-SPECIFICATION.md → Stage 5  
**Autonomous**: Yes

```python
success = orchestrator.run_stage_5_validation()
```

**This Stage Does**:

- ✅ Task 5.1: Full file integrity validation (frontmatter, tags, layers, UTF-8, size)
- ✅ Task 5.2: Cross-file consistency check (duplicates, batch IDs, dates, sources)
- ✅ Task 5.3: Tag coverage analysis (statistics, anomalies, quality)
- ✅ Task 5.4: Generates comprehensive import report

**Validation Checks**:

- ✅ All files readable and valid UTF-8
- ✅ Layer 1 frontmatter present and valid YAML
- ✅ Layer 2 tags all in valid format
- ✅ Layer 3 placeholder structure intact
- ✅ No duplicate files
- ✅ Consistent import batch ID
- ✅ No files > 5MB
- ✅ No files < 2 tags (should have at least source + proficiency)

**Output Files Generated**:

- `integrity-validation.csv` - File integrity results
- `consistency-validation.csv` - Batch-level consistency
- `tag-coverage-analysis.csv` - Tag statistics and distribution
- `tag-anomalies.csv` - Over/under-tagged files
- `import-batch-report.md` - **Comprehensive deployment report**

**Report Shows**:

```
Status: ✅ READY FOR DEPLOYMENT
- Files processed: 600
- Integrity passed: 598/600 (99.7%)
- Consistency passed: 4/4 (100%)
- Anomalies: 2 (< 1%)
```

**Checkpoint**: Read deployment status from report

```python
# Read report
with open("output/stage_5_validation/import-batch-report.md") as f:
    report = f.read()

if "✅ READY FOR DEPLOYMENT" in report:
    logger.info("✅ BATCH READY FOR PRODUCTION DEPLOYMENT")
    return True
else:
    logger.warning("⚠️  REVIEW REQUIRED - Do not deploy yet")
    logger.warning("Review anomalies in:")
    print(" - integrity-validation.csv")
    print(" - consistency-validation.csv")
    print(" - tag-anomalies.csv")
    return False
```

**Allowed To Continue If**:

- Status is "✅ READY FOR DEPLOYMENT"
- Integrity check: < 1% failures
- Consistency check: 100% pass
- Anomalies: < 5 files

---

## TASK 7: FINALIZE PROCESSED FILES

**Time**: 5 minutes  
**Autonomous**: Yes

```python
orchestrator.finalize()
```

**This Creates**:

- `processed_batch_files/` directory with all 600 processed, validated files ready for deployment

**Verification**:

```bash
ls -la processed_batch_files/ | wc -l  # Should match source file count
head -20 processed_batch_files/sample.md  # Verify Layer 1 + Layer 2 applied
```

---

## TASK 8: GENERATE FINAL SUMMARY FOR HUMAN

**Time**: 2 minutes  
**Autonomous**: Yes (provides handoff summary)

**Create Summary Report**:

```
BATCH IMPORT COMPLETE: {batch_id}

Source: {source_type}
Files Processed: {total_files}
Duration: {elapsed_time}

QUALITY METRICS:
✅ Integrity: {passed}/{total} files
✅ Consistency: All checks passed
✅ Tag Coverage: {coverage}% with valid tags
⚠️  Anomalies: {count} files flagged for review

DEPLOYMENT READY: {status}

Next Steps:
1. Review import-batch-report.md if any anomalies
2. Backup existing Logseq graph
3. Deploy processed files to ~/Logseq/graph/pages/
4. Re-index in Logseq (Settings → Advanced → Clear caches)
5. Verify import (search #source/{source_type})

Report Location: {report_path}
Processed Files Location: {processed_files_path}
```

---

## ERROR RECOVERY PROCEDURES

### If Stage Fails

**For ANY stage failure**:

1. Check `import-orchestration.log` for detailed error
2. Identify which task within stage failed
3. Review corresponding CSV error files
4. Take corrective action:
   - **Stage 1**: Manual review files in linting-review-required.csv
   - **Stage 2**: Fix date format issues in hierarchy-mapping.csv
   - **Stage 3**: Fix tag format issues in tags-validation-failures.csv
   - **Stage 4**: Less critical - can proceed with warnings
   - **Stage 5**: DO NOT DEPLOY if validation fails

5. Restart from failed stage only (don't re-run previous stages)

### Example: Handling Stage 2 Failure

```python
# If Stage 2 validation shows date format errors:
import pandas as pd

failures = pd.read_csv("output/stage_2_layer1/layer1-validation-results.csv")
failed_files = failures[failures['status'] == 'FAIL']

# Fix manually (or remove bad files and re-run Stage 2 only)
for _, file_row in failed_files.iterrows():
    # Fix or remove file
    pass

# Re-run only Stage 2
success = orchestrator.run_stage_2_layer1()
```

---

## SUCCESS CRITERIA CHECKLIST

Before declaring import complete:

- [ ] All 5 stages completed successfully
- [ ] `import-batch-report.md` shows "✅ READY FOR DEPLOYMENT"
- [ ] `integrity-validation.csv`: 100% or 99%+ pass rate
- [ ] `consistency-validation.csv`: All checks passed
- [ ] `tag-anomalies.csv`: < 5 files flagged
- [ ] `processed_batch_files/` contains all source files
- [ ] All files have Layer 1 frontmatter (YAML)
- [ ] All files have Layer 2 tags section
- [ ] All files have Layer 3 placeholder sections
- [ ] No files are > 5MB
- [ ] Logging shows no critical errors

---

## AUTONOMOUS EXECUTION TEMPLATE

```python
#!/usr/bin/env python3
"""Autonomous batch import execution for LLM agents."""

import sys
from pathlib import Path
from scripts.orchestrate_import import ImportOrchestrator

def main():
    # Configuration
    source_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/source")
    source_type = sys.argv[2] if len(sys.argv) > 2 else "lighthouse_labs"
    batch_id = sys.argv[3] if len(sys.argv) > 3 else "autonomous-batch-1"
    output_dir = Path(sys.argv[4] if len(sys.argv) > 4 else "/tmp/output")
    
    # Initialize
    orchestrator = ImportOrchestrator(
        source_dir=source_dir,
        source_type=source_type,
        batch_id=batch_id,
        output_dir=output_dir,
        config_path="scripts/config.json"
    )
    
    # Execute pipeline
    success = orchestrator.run()
    
    if success:
        print(f"✅ Import complete: {batch_id}")
        print(f"📁 Processed files: {output_dir / 'processed_batch_files'}")
        print(f"📊 Report: {output_dir / 'stage_5_validation' / 'import-batch-report.md'}")
        return 0
    else:
        print(f"❌ Import failed: {batch_id}")
        print(f"📋 Check logs: {output_dir / 'import-orchestration.log'}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

**Usage**:

```bash
python3 autonomous_import.py /path/to/source lighthouse_labs batch-1 /path/to/output
```

---

## HUMAN HANDOFF

After completion, provide human with:

1. **Import Report**
   - File: `stage_5_validation/import-batch-report.md`
   - Shows: Deployment status, quality metrics, next steps

2. **Quality Metrics**
   - File: `stage_5_validation/tag-coverage-analysis.csv`
   - Shows: Tag distribution, coverage percentages

3. **Any Issues**
   - Files: `tag-anomalies.csv`, `integrity-validation.csv` (if any failures)
   - Shows: Which files need manual review

4. **Processed Files**
   - Directory: `processed_batch_files/`
   - Contains: All 600+ ready-to-deploy files with three layers applied

5. **Next Actions**
   - Deploy to Logseq using provided instructions
   - Monitor for any anomalies
   - Begin Layer 3 population as user reviews

---

**Status**: ✅ Ready for Autonomous Execution

This task list enables any LLM agent to independently execute complete batch imports with quality assurance and clear checkpoints for human review.
