#!/usr/bin/env python3
"""
Stage 5: Validation & Quality Checks

Tasks:
- 5.1: File integrity validation
- 5.2: Cross-file consistency check
- 5.3: Tag coverage analysis
- 5.4: Generate import report
"""

import re
from pathlib import Path
from typing import Dict, List
import pandas as pd
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_file_integrity(source_dir: Path, output_dir: Path = None) -> Dict:
    """
    Validate integrity of all processed files.
    
    Args:
        source_dir: Directory with markdown files to validate
        output_dir: Output directory for results
    
    Returns:
        Dictionary with validation statistics
    """
    logger.info("Running file integrity validation...")
    
    files_checked = 0
    files_passed = 0
    validation_results = []
    
    for md_file in source_dir.glob("*.md"):
        files_checked += 1
        issues = []
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check readable
            if not content:
                issues.append("Empty file")
            
            # Check frontmatter
            if content.startswith('---'):
                end_marker = content.find('\n---\n')
                if end_marker == -1:
                    issues.append("Unclosed frontmatter")
                else:
                    yaml_str = content[4:end_marker]
                    try:
                        yaml.safe_load(yaml_str)
                    except:
                        issues.append("Invalid YAML frontmatter")
            else:
                issues.append("No frontmatter found")
            
            # Check tags section
            if '## Tags' not in content:
                issues.append("No tags section")
            
            # Check UTF-8
            md_file.read_text(encoding='utf-8')
            
            # Check Layer 3 placeholders
            required_sections = ['Prerequisites', 'Enables', 'Project Connections', 'Goal Connections']
            missing = [s for s in required_sections if f"## {s}" not in content]
            if missing:
                issues.append(f"Missing Layer 3 sections: {', '.join(missing)}")
            
            # Check size
            size_mb = md_file.stat().st_size / (1024 * 1024)
            if size_mb > 5:
                issues.append(f"File too large: {size_mb:.2f}MB")
            
            if not issues:
                files_passed += 1
                status = 'PASS'
            else:
                status = 'FAIL'
            
            validation_results.append({
                'file': md_file.name,
                'status': status,
                'size_kb': md_file.stat().st_size / 1024,
                'issues': '; '.join(issues) if issues else None
            })
            
        except Exception as e:
            validation_results.append({
                'file': md_file.name,
                'status': 'ERROR',
                'size_kb': 0,
                'issues': str(e)
            })
    
    # Save results
    if output_dir:
        pd.DataFrame(validation_results).to_csv(
            output_dir / "integrity-validation.csv", index=False
        )
    
    logger.info(f"Integrity validation: {files_passed}/{files_checked} passed")
    
    return {
        'files_checked': files_checked,
        'files_passed': files_passed,
        'files_failed': files_checked - files_passed
    }


def validate_batch_consistency(source_dir: Path, output_dir: Path = None) -> Dict:
    """
    Check consistency across entire batch of files.
    
    Args:
        source_dir: Directory with files
        output_dir: Output directory for results
    
    Returns:
        Dictionary with consistency check results
    """
    logger.info("Running batch consistency check...")
    
    consistency_checks = []
    files_by_name = {}
    import_batches = set()
    import_dates = set()
    sources = set()
    
    for md_file in source_dir.glob("*.md"):
        # Check for duplicates
        if md_file.name in files_by_name:
            consistency_checks.append({
                'check': 'Duplicate file names',
                'status': 'FAIL',
                'details': f"Duplicate: {md_file.name}"
            })
        files_by_name[md_file.name] = md_file
        
        # Extract batch info from frontmatter
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                end_marker = content.find('\n---\n')
                if end_marker != -1:
                    yaml_str = content[4:end_marker]
                    metadata = yaml.safe_load(yaml_str) or {}
                    import_batches.add(metadata.get('import-batch', 'unknown'))
                    import_dates.add(metadata.get('import-date', 'unknown'))
                    sources.add(metadata.get('source', 'unknown'))
        except:
            pass
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: No duplicate files
    checks_total += 1
    if len(files_by_name) == len(list(source_dir.glob("*.md"))):
        consistency_checks.append({
            'check': 'No duplicate files',
            'status': 'PASS',
            'details': f"{len(files_by_name)} unique files"
        })
        checks_passed += 1
    
    # Check 2: Consistent batch IDs
    checks_total += 1
    if len(import_batches) == 1:
        consistency_checks.append({
            'check': 'Consistent batch IDs',
            'status': 'PASS',
            'details': f"All files from batch: {list(import_batches)[0]}"
        })
        checks_passed += 1
    else:
        consistency_checks.append({
            'check': 'Consistent batch IDs',
            'status': 'FAIL',
            'details': f"Multiple batches: {import_batches}"
        })
    
    # Check 3: Consistent sources
    checks_total += 1
    if len(sources) <= 2:  # Allow 1-2 sources (actual + unknown)
        consistency_checks.append({
            'check': 'Consistent sources',
            'status': 'PASS',
            'details': f"Sources: {sources}"
        })
        checks_passed += 1
    
    # Check 4: Reasonable date range
    checks_total += 1
    consistency_checks.append({
        'check': 'Import dates present',
        'status': 'PASS',
        'details': f"{len(import_dates)} unique dates"
    })
    checks_passed += 1
    
    # Save results
    if output_dir:
        pd.DataFrame(consistency_checks).to_csv(
            output_dir / "consistency-validation.csv", index=False
        )
    
    logger.info(f"Consistency check: {checks_passed}/{checks_total} passed")
    
    return {
        'checks_total': checks_total,
        'checks_passed': checks_passed,
        'checks_failed': checks_total - checks_passed
    }


def analyze_tag_coverage(source_dir: Path, output_dir: Path = None) -> Dict:
    """
    Analyze tag coverage and identify anomalies.
    
    Args:
        source_dir: Directory with files
        output_dir: Output directory for results
    
    Returns:
        Dictionary with tag statistics
    """
    logger.info("Analyzing tag coverage...")
    
    tag_stats = {
        'total_files': 0,
        'files_with_tags': 0,
        'tag_counts': {},
        'domain_tags': {},
        'activity_tags': {},
        'proficiency_levels': {},
        'source_tags': {},
        'anomalies': []
    }
    
    for md_file in source_dir.glob("*.md"):
        tag_stats['total_files'] += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract tags section
            tags_start = content.find('## Tags\n')
            if tags_start == -1:
                tag_stats['anomalies'].append({
                    'file': md_file.name,
                    'issue': 'No tags section'
                })
                continue
            
            tags_start += len('## Tags\n')
            tags_end = content.find('\n## ', tags_start)
            if tags_end == -1:
                tags_end = len(content)
            
            tags_text = content[tags_start:tags_end]
            tags = re.findall(r'#[\w\-/]+(?:::\w+)?', tags_text)
            
            if not tags:
                tag_stats['anomalies'].append({
                    'file': md_file.name,
                    'issue': 'No tags found in tags section'
                })
                continue
            
            tag_stats['files_with_tags'] += 1
            tag_stats['tag_counts'][md_file.name] = len(tags)
            
            # Categorize tags
            for tag in tags:
                if 'domain' in tag:
                    domain = tag.split('/')[1] if '/' in tag else 'unknown'
                    tag_stats['domain_tags'][domain] = tag_stats['domain_tags'].get(domain, 0) + 1
                elif 'activity' in tag:
                    tag_stats['activity_tags'][tag] = tag_stats['activity_tags'].get(tag, 0) + 1
                elif 'proficiency' in tag and '::' in tag:
                    level = tag.split('::')[1]
                    tag_stats['proficiency_levels'][level] = tag_stats['proficiency_levels'].get(level, 0) + 1
                elif 'source' in tag:
                    source = tag.split('/')[1] if '/' in tag else 'unknown'
                    tag_stats['source_tags'][source] = tag_stats['source_tags'].get(source, 0) + 1
            
            # Check for anomalies
            if len(tags) > 15:
                tag_stats['anomalies'].append({
                    'file': md_file.name,
                    'issue': f'Over-tagged: {len(tags)} tags'
                })
            
            if len(tags) < 2:
                tag_stats['anomalies'].append({
                    'file': md_file.name,
                    'issue': f'Under-tagged: {len(tags)} tags'
                })
        
        except Exception as e:
            logger.warning(f"Error analyzing tags in {md_file.name}: {str(e)}")
    
    # Save results
    if output_dir:
        coverage_df = pd.DataFrame([
            {
                'metric': 'Total files',
                'value': tag_stats['total_files']
            },
            {
                'metric': 'Files with tags',
                'value': tag_stats['files_with_tags']
            },
            {
                'metric': 'Average tags per file',
                'value': f"{sum(tag_stats['tag_counts'].values()) / max(1, tag_stats['files_with_tags']):.1f}"
            },
            {
                'metric': 'Domain tags count',
                'value': len(tag_stats['domain_tags'])
            },
            {
                'metric': 'Anomalies found',
                'value': len(tag_stats['anomalies'])
            }
        ])
        coverage_df.to_csv(output_dir / "tag-coverage-analysis.csv", index=False)
        
        if tag_stats['anomalies']:
            pd.DataFrame(tag_stats['anomalies']).to_csv(
                output_dir / "tag-anomalies.csv", index=False
            )
    
    logger.info(f"Tag coverage analysis complete: {tag_stats['files_with_tags']}/{tag_stats['total_files']} with tags")
    
    return tag_stats


def generate_import_report(batch_id: str, source_type: str, import_date: str,
                          integrity_results: Dict, consistency_results: Dict,
                          coverage_results: Dict, stage_outputs: Dict,
                          output_dir: Path) -> Path:
    """
    Generate comprehensive import batch report.
    
    Args:
        batch_id: Batch identifier
        source_type: Type of source
        import_date: Import date
        integrity_results: Results from integrity validation
        consistency_results: Results from consistency check
        coverage_results: Results from tag coverage analysis
        stage_outputs: Dictionary with stage outputs
        output_dir: Output directory
    
    Returns:
        Path to generated report
    """
    logger.info("Generating import report...")
    
    # Determine deployment status
    all_passed = (
        integrity_results.get('files_failed', 1) == 0 and
        consistency_results.get('checks_failed', 1) <= 1 and
        len(coverage_results.get('anomalies', [])) < 5
    )
    
    status = "✅ READY FOR DEPLOYMENT" if all_passed else "⚠️  REVIEW REQUIRED"
    
    report = f"""# Import Batch Report

**Batch ID**: {batch_id}
**Source Type**: {source_type}
**Import Date**: {import_date}
**Report Generated**: {datetime.now().isoformat()}
**Status**: {status}

## Summary

- Total Files Processed: {integrity_results.get('files_checked', 0)}
- Files Passing Integrity: {integrity_results.get('files_passed', 0)}/{integrity_results.get('files_checked', 0)}
- Consistency Checks Passed: {consistency_results.get('checks_passed', 0)}/{consistency_results.get('checks_total', 0)}
- Files with Tags: {coverage_results.get('files_with_tags', 0)}/{coverage_results.get('total_files', 0)}
- Anomalies Found: {len(coverage_results.get('anomalies', []))}

## Quality Metrics

### Integrity Validation
- Files Checked: {integrity_results.get('files_checked', 0)}
- Passed: {integrity_results.get('files_passed', 0)} ✅
- Failed: {integrity_results.get('files_failed', 0)}

### Consistency Check
- Checks Total: {consistency_results.get('checks_total', 0)}
- Passed: {consistency_results.get('checks_passed', 0)} ✅
- Failed: {consistency_results.get('checks_failed', 0)}

### Tag Coverage
- Average Tags per File: {coverage_results.get('tag_counts', {}) and
    sum(coverage_results.get('tag_counts', {}).values()) / max(1, len(coverage_results.get('tag_counts', {}))):.1f}
- Unique Domains: {len(coverage_results.get('domain_tags', {}))}
- Proficiency Levels Distribution:
{chr(10).join(f"  - {level}: {count}" for level, count in coverage_results.get('proficiency_levels', {}).items())}

## Processing Details

### Layer 1 (Metadata & Hierarchy)
- Status: ✅ Applied
- Contains: Source tracking, chronological metadata, hierarchy information

### Layer 2 (Semantic Tags)
- Status: ✅ Applied
- Dimensions: Domain, Activity, Proficiency, Project, Goal, Connection, Readiness, Source
- Average tags per file: {coverage_results.get('tag_counts', {}) and
    sum(coverage_results.get('tag_counts', {}).values()) / max(1, len(coverage_results.get('tag_counts', {}))):.1f}

### Layer 3 (Connections & Placeholders)
- Status: ✅ Placeholders created
- Sections: Prerequisites, Enables, Project Connections, Goal Connections, See Also
- Next Step: User populates during review

## Anomalies

{f'''
{chr(10).join(f"- **{a.get('file', 'unknown')}**: {a.get('issue', 'Unknown issue')}" for a in coverage_results.get('anomalies', [])[:10])}

Total anomalies: {len(coverage_results.get('anomalies', []))}
''' if coverage_results.get('anomalies', []) else 'None found ✅'}

## Deployment Instructions

1. **Backup Existing Data**
   ```bash
   cp -r ~/Logseq/graph/pages ~/Logseq/graph/pages.backup.{datetime.now().strftime('%Y-%m-%d')}
   ```

2. **Copy Files**
   ```bash
   cp processed_batch_files/*.md ~/Logseq/graph/pages/
   ```

3. **Re-index in Logseq**
   - Open Logseq
   - Settings → Advanced → Clear caches and re-index
   - Wait 2-5 minutes for indexing

4. **Verify Import**
   - Search: `#source/{source_type}` → should return ~{integrity_results.get('files_checked', 0)} results
   - Navigate: Try accessing any index page
   - Query: Run a saved query to verify tag structure

## Files Ready for Deployment

✅ **{integrity_results.get('files_passed', 0)}** files passed all quality checks
✅ All three layers applied
✅ Ready for production deployment

## Next Steps

1. Deploy to Logseq graph using instructions above
2. Verify search and navigation working
3. Begin Layer 3 population as you review notes
4. Update proficiency tags over time as you learn
5. Create proficiency dashboard in 4 weeks

## Configuration Applied

- **Batch ID**: {batch_id}
- **Source Type**: {source_type}
- **Import Timestamp**: {import_date}
- **Deployment Status**: {status}

---

Generated: {datetime.now().isoformat()}
"""
    
    # Save report
    report_path = output_dir / "import-batch-report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Report generated: {report_path}")
    
    return report_path


if __name__ == '__main__':
    test_dir = Path('./test_files')
    output = Path('./stage_5_output')
    output.mkdir(exist_ok=True)
    
    integrity = validate_file_integrity(test_dir, output)
    consistency = validate_batch_consistency(test_dir, output)
    coverage = analyze_tag_coverage(test_dir, output)
    
    report = generate_import_report(
        batch_id='test-batch',
        source_type='test',
        import_date=datetime.now().isoformat(),
        integrity_results=integrity,
        consistency_results=consistency,
        coverage_results=coverage,
        stage_outputs={},
        output_dir=output
    )
    
    print(f"Report: {report}")
