# Import Pipeline Setup & Testing Guide

## Directory Structure

Before running the import, ensure this structure exists:

```
scripts/
├── orchestrate_import.py           # Main orchestrator
├── stage_1_quality_assurance.py    # Markdown QA module
├── stage_2_layer1_metadata.py      # Layer 1 metadata module
├── stage_3_layer2_tagging.py       # Layer 2 tagging module
├── stage_4_layer3_placeholders.py  # Layer 3 placeholders module
├── stage_5_validation.py           # Validation module
├── config.json                      # Main configuration
├── dictionaries/
│   ├── custom-dictionary.json       # Custom terms for spell check
│   └── technical-terms.json         # Technical terms database
├── schemas/
│   └── tag-schema.json              # Tag schema definition
├── tag-mappings/
│   └── lighthouse-labs-domain-mapping.csv  # Domain mappings
└── metadata/
    ├── projects-list.json           # Known projects
    ├── goals-list.json              # User's goals
    └── graph-structure-map.json     # Existing graph structure
```

## Prerequisites

Install required Python packages:

```bash
pip install pandas pyyaml spellchecker
```

## Usage: Quick Start

### 1. Prepare Your Source Files

Place all markdown files to be imported in a source directory:

```bash
mkdir -p /tmp/lighthouse_batch_1
cp /path/to/lighthouse/files/*.md /tmp/lighthouse_batch_1/
```

### 2. Run the Import Pipeline

```bash
cd scripts

python3 orchestrate_import.py \
  --source-dir /tmp/lighthouse_batch_1 \
  --source-type lighthouse_labs \
  --batch-id lighthouse-labs-batch-1 \
  --output-dir /tmp/lighthouse_batch_1_output \
  --config config.json
```

### 3. Review Output

Check the generated report:

```bash
cat /tmp/lighthouse_batch_1_output/stage_5_validation/import-batch-report.md
```

### 4. Deploy to Logseq

```bash
# Backup first
cp -r ~/Logseq/graph/pages ~/Logseq/graph/pages.backup.2025-12-18

# Copy processed files
cp /tmp/lighthouse_batch_1_output/processed_batch_files/*.md ~/Logseq/graph/pages/

# Re-index in Logseq
# Settings → Advanced → Clear caches and re-index
```

---

## Usage: Testing with Sample Files

### Test on 10 Sample Files

```bash
# Create test directory with sample files
mkdir -p /tmp/test_import
cp /tmp/lighthouse_batch_1/*.md /tmp/test_import/ | head -10

# Run test import
python3 orchestrate_import.py \
  --source-dir /tmp/test_import \
  --source-type lighthouse_labs \
  --batch-id test-batch-1 \
  --output-dir /tmp/test_import_output \
  --config config.json
```

### Review Test Results

```bash
# Check summary report
cat /tmp/test_import_output/stage_5_validation/import-batch-report.md

# Check detailed results
ls -la /tmp/test_import_output/stage_*/

# Review any validation issues
cat /tmp/test_import_output/stage_5_validation/integrity-validation.csv
```

### Verify Processing

```bash
# Sample processed file
head -50 /tmp/test_import_output/processed_batch_files/sample-file.md
```

---

## Advanced: Running Individual Stages

### Stage 1: Quality Assurance

```python
from stage_1_quality_assurance import (
    identify_files, lint_markdown, normalize_spelling, 
    extract_existing_metadata
)
from pathlib import Path

source = Path('/tmp/lighthouse_batch_1')
output = Path('/tmp/stage_1_output')
output.mkdir(exist_ok=True)

# Run all tasks
manifest = identify_files(source, output)
print(f"Found {len(manifest)} files")

lint_results = lint_markdown(source, output)
print(f"Linting: {lint_results}")

spell_results = normalize_spelling(source, None, output)
print(f"Spelling: {spell_results}")

metadata = extract_existing_metadata(source, output)
print(f"Metadata: {len(metadata)} files processed")
```

### Stage 2: Layer 1 Metadata

```python
from stage_2_layer1_metadata import (
    map_file_to_hierarchy, build_layer1_frontmatter, validate_layer1
)
from datetime import datetime

hierarchy = map_file_to_hierarchy(manifest, 'lighthouse_labs', output)
print(f"Hierarchy mapped for {len(hierarchy)} files")

layer1_result = build_layer1_frontmatter(
    source, hierarchy, 'test-batch', 
    datetime.now().isoformat(), output
)
print(f"Layer 1: {layer1_result}")

validation = validate_layer1(output, output)
print(f"Validation: {validation}")
```

### Stage 3: Layer 2 Tagging

```python
from stage_3_layer2_tagging import (
    extract_keywords, map_keywords_to_tags, validate_tags
)

keywords = extract_keywords(output, None, None, output)
print(f"Keywords: {keywords}")

tagging = map_keywords_to_tags(
    output, output / 'content-keywords.csv',
    'lighthouse_labs', None, None, output
)
print(f"Tagging: {tagging}")

tag_validation = validate_tags(output, output / 'tags-mapped.csv', None, output)
print(f"Tag Validation: {tag_validation}")
```

### Stage 4: Layer 3 Placeholders

```python
from stage_4_layer3_placeholders import (
    detect_layer3_connections, build_layer3_placeholders, validate_layer3
)

connections = detect_layer3_connections(output, None, output)
print(f"Connections detected: {connections}")

placeholders = build_layer3_placeholders(
    output, output / 'layer3-candidates.csv', output
)
print(f"Placeholders: {placeholders}")

layer3_validation = validate_layer3(output, output)
print(f"Layer 3 validation: {layer3_validation}")
```

### Stage 5: Validation & Report

```python
from stage_5_validation import (
    validate_file_integrity, validate_batch_consistency,
    analyze_tag_coverage, generate_import_report
)

integrity = validate_file_integrity(output, output)
consistency = validate_batch_consistency(output, output)
coverage = analyze_tag_coverage(output, output)

report = generate_import_report(
    batch_id='test-batch',
    source_type='lighthouse_labs',
    import_date=datetime.now().isoformat(),
    integrity_results=integrity,
    consistency_results=consistency,
    coverage_results=coverage,
    stage_outputs={},
    output_dir=output
)

print(f"Report: {report}")
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Solution**: Install required packages
```bash
pip install pandas pyyaml spellchecker
```

### Issue: Files not found in source directory

**Solution**: Verify path exists and contains .md files
```bash
ls -la /path/to/source/
find /path/to/source/ -name "*.md" | wc -l
```

### Issue: Validation fails with "Unclosed frontmatter"

**Solution**: Check frontmatter format in processed files
```bash
head -20 /path/to/problematic/file.md
```

YAML frontmatter must be properly closed with `---` on its own line.

### Issue: "Invalid tag format" errors

**Solution**: Review tag-schema.json for valid formats
```bash
cat schemas/tag-schema.json | grep -A5 '"format"'
```

Tags must follow format: `#dimension/path::level` (if applicable)

### Issue: No files processed

**Solution**: Check if files are actually .md and readable
```bash
file /path/to/source/*.md
chmod +r /path/to/source/*.md
```

---

## Configuration Customization

### Add Custom Domain Mapping

Edit `tag-mappings/lighthouse-labs-domain-mapping.csv`:

```csv
course_pattern,domain_tag
Course 1,#domain/it-essentials
Course 2,#domain/networking
Course 3,#domain/cybersecurity
```

### Add Custom Technical Terms

Edit `dictionaries/technical-terms.json`:

```json
{
  "technical_terms": [
    "YourTerm",
    "AnotherTerm"
  ]
}
```

### Update Goals List

Edit `metadata/goals-list.json`:

```json
{
  "goals": [
    {
      "id": "security-analyst",
      "name": "Become Security Analyst",
      "priority": "high"
    }
  ]
}
```

---

## Batch Processing Multiple Imports

### Process Multiple Batches Sequentially

```bash
#!/bin/bash

BATCHES=(
    "lighthouse_batch_1:lighthouse-labs:/path/to/lighthouse1"
    "lighthouse_batch_2:lighthouse-labs:/path/to/lighthouse2"
    "perplexity_batch_1:perplexity:/path/to/perplexity"
)

for batch_config in "${BATCHES[@]}"; do
    IFS=':' read batch_id source_type source_dir <<< "$batch_config"
    
    python3 orchestrate_import.py \
        --source-dir "$source_dir" \
        --source-type "$source_type" \
        --batch-id "$batch_id" \
        --output-dir "/tmp/${batch_id}_output" \
        --config config.json
    
    if [ $? -eq 0 ]; then
        echo "✅ $batch_id completed successfully"
    else
        echo "❌ $batch_id failed"
        exit 1
    fi
done

echo "✅ All batches processed"
```

### Process in Parallel (Experimental)

```bash
#!/bin/bash

# Process multiple batches in parallel (use with caution!)
python3 orchestrate_import.py --source-dir /tmp/batch1 --batch-id batch-1 &
python3 orchestrate_import.py --source-dir /tmp/batch2 --batch-id batch-2 &

wait

echo "✅ All batches processed"
```

---

## Monitoring & Logs

### View Live Import Log

```bash
tail -f import-orchestration.log
```

### Check Processing Statistics

```bash
# Count files processed
wc -l /tmp/output/stage_*/import-manifest.csv

# Show validation summary
cat /tmp/output/stage_5_validation/integrity-validation.csv | tail -5
```

### Generate Processing Report

```bash
# Files by stage
for stage in stage_*; do
    echo "=== $stage ==="
    ls -la $stage/*.csv | wc -l
done
```

---

## Next: Automating Regular Imports

After testing is complete, you can:

1. Schedule regular batch processing
2. Create automated quality checks
3. Set up Logseq sync integration
4. Build dashboards tracking import statistics

See `30-DAY-IMPLEMENTATION-ROADMAP.md` for long-term strategy.

---

## Getting Help

If you encounter issues:

1. Check logs: `tail -50 import-orchestration.log`
2. Review validation CSVs in output directory
3. Inspect a sample processed file
4. Verify configuration in `config.json`
5. Check `BATCH-IMPORT-TASK-SPECIFICATION.md` for detailed task descriptions

---

**Ready to test?** Start with 10 sample files using the testing commands above!
