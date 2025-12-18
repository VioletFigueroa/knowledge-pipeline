#!/usr/bin/env python3
"""
Stage 2: Metadata Extraction & Layer 1 Population

Tasks:
- 2.1: Map file to source hierarchy
- 2.2: Build Layer 1 frontmatter
- 2.3: Validate Layer 1 integrity
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import yaml
import logging

logger = logging.getLogger(__name__)


# Task 2.1: Map Hierarchy
# =========================================================================

def parse_lighthouse_path(file_path: str) -> Dict:
    """Parse Lighthouse Labs file structure."""
    hierarchy = {}
    
    # Pattern: Course_X/Week_Y/filename.md or similar variations
    parts = file_path.split('/')
    
    for part in parts:
        if part.lower().startswith('course'):
            match = re.search(r'course[_\s]*(\d+)', part, re.IGNORECASE)
            if match:
                hierarchy['course'] = int(match.group(1))
        elif part.lower().startswith('week'):
            match = re.search(r'week[_\s]*(\d+)', part, re.IGNORECASE)
            if match:
                hierarchy['week'] = int(match.group(1))
    
    # Extract topic from filename
    filename = Path(file_path).stem
    hierarchy['topic'] = filename.replace('_', ' ').title()
    
    return hierarchy


def parse_perplexity_path(file_path: str) -> Dict:
    """Parse Perplexity research file structure."""
    hierarchy = {}
    
    parts = file_path.split('/')
    
    # Try to extract chat ID and topic
    if len(parts) >= 2:
        hierarchy['source'] = 'Perplexity'
        hierarchy['category'] = parts[0].title()
        hierarchy['topic'] = Path(parts[-1]).stem.replace('_', ' ').title()
    
    return hierarchy


def parse_journal_path(file_path: str) -> Dict:
    """Parse journal file structure."""
    hierarchy = {}
    
    filename = Path(file_path).stem
    
    # Look for date patterns: YYYY_MM_DD, YYYY-MM-DD, daily.journal.YYYY.MM.DD, etc.
    date_match = re.search(
        r'(\d{4})[_\-](\d{1,2})[_\-](\d{1,2})',
        filename
    )
    
    if date_match:
        year, month, day = date_match.groups()
        hierarchy['year'] = year
        hierarchy['month'] = month.zfill(2)
        hierarchy['day'] = day.zfill(2)
        hierarchy['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        hierarchy['type'] = 'journal'
    else:
        hierarchy['type'] = 'note'
        hierarchy['topic'] = filename.replace('_', ' ').replace('-', ' ').title()
    
    return hierarchy


def map_file_to_hierarchy(manifest_df: pd.DataFrame, source_type: str, 
                         output_dir: Path) -> pd.DataFrame:
    """
    Map each file to its source hierarchy.
    
    Args:
        manifest_df: DataFrame from Stage 1.1 with file manifest
        source_type: Type of source (lighthouse_labs, perplexity, journals, etc.)
        output_dir: Directory to save hierarchy mapping
    
    Returns:
        DataFrame with hierarchy mapping
    """
    logger.info(f"Mapping {len(manifest_df)} files to hierarchy (source_type: {source_type})")
    
    hierarchies = []
    
    # Select parser based on source type
    if source_type == 'lighthouse_labs':
        parser = parse_lighthouse_path
    elif source_type == 'perplexity':
        parser = parse_perplexity_path
    elif source_type == 'journals':
        parser = parse_journal_path
    else:
        # Generic parser
        parser = lambda path: {'topic': Path(path).stem.replace('_', ' ').title()}
    
    for _, row in manifest_df.iterrows():
        file_path = row['source_file']
        hierarchy = parser(file_path)
        hierarchy['file_name'] = Path(file_path).name
        hierarchy['source_file_path'] = file_path
        hierarchies.append(hierarchy)
    
    df = pd.DataFrame(hierarchies)
    df.to_csv(output_dir / "hierarchy-mapping.csv", index=False)
    logger.info(f"Hierarchy mapping created: {len(df)} files mapped")
    
    return df


# Task 2.2: Build Layer 1 Frontmatter
# =========================================================================

def build_layer1_frontmatter_dict(hierarchy: Dict, batch_id: str, 
                                import_date: str, source_type: str) -> Dict:
    """
    Build Layer 1 frontmatter dictionary.
    
    Args:
        hierarchy: Hierarchy information for file
        batch_id: Import batch identifier
        import_date: Import date (ISO format)
        source_type: Type of source material
    
    Returns:
        Dictionary with Layer 1 frontmatter
    """
    frontmatter = {
        'source': source_type,
        'source-file-original': hierarchy.get('source_file_path', ''),
        'hierarchy': {},
        'created-date': None,
        'created-chronological': None,
        'last-modified': datetime.now().isoformat(),
        'import-date': import_date,
        'import-batch': batch_id,
        'status': 'imported'
    }
    
    # Build hierarchy field
    if 'course' in hierarchy and 'week' in hierarchy:
        frontmatter['hierarchy'] = {
            'level': ['course', 'week', 'topic'],
            'course': hierarchy.get('course'),
            'week': hierarchy.get('week'),
            'topic': hierarchy.get('topic')
        }
        frontmatter['hierarchy-full'] = \
            f"Course {hierarchy.get('course')} > Week {hierarchy.get('week')} > {hierarchy.get('topic')}"
    
    elif 'date' in hierarchy:
        # Journal file
        frontmatter['hierarchy'] = {
            'level': ['year', 'month', 'day'],
            'year': hierarchy.get('year'),
            'month': hierarchy.get('month'),
            'day': hierarchy.get('day')
        }
        frontmatter['hierarchy-full'] = \
            f"{hierarchy.get('year')}-{hierarchy.get('month')}-{hierarchy.get('day')}"
        frontmatter['created-date'] = hierarchy.get('date')
    
    elif 'category' in hierarchy:
        # Perplexity or other categorized
        frontmatter['hierarchy'] = {
            'level': ['category', 'topic'],
            'category': hierarchy.get('category'),
            'topic': hierarchy.get('topic')
        }
        frontmatter['hierarchy-full'] = \
            f"{hierarchy.get('category')} > {hierarchy.get('topic')}"
    
    else:
        # Generic
        frontmatter['hierarchy'] = {
            'level': ['topic'],
            'topic': hierarchy.get('topic')
        }
        frontmatter['hierarchy-full'] = hierarchy.get('topic')
    
    # Calculate chronological date if not set
    if not frontmatter['created-chronological']:
        try:
            if frontmatter['created-date']:
                date_obj = datetime.fromisoformat(frontmatter['created-date'])
            else:
                date_obj = datetime.now()
            
            # Calculate ISO week
            iso_year, iso_week, _ = date_obj.isocalendar()
            frontmatter['created-chronological'] = f"{iso_year}-W{iso_week:02d}"
        except:
            frontmatter['created-chronological'] = datetime.now().strftime('%Y-W%V')
    
    return frontmatter


def apply_layer1_to_file(file_path: Path, frontmatter_dict: Dict) -> str:
    """
    Add Layer 1 frontmatter to file content.
    
    Args:
        file_path: Path to markdown file
        frontmatter_dict: Frontmatter dictionary
    
    Returns:
        Content with frontmatter prepended
    """
    # Read existing content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip existing frontmatter
    if content.startswith('---'):
        # Find end of existing frontmatter
        end_marker = content.find('\n---\n')
        if end_marker != -1:
            content = content[end_marker + 5:]
    
    # Generate YAML frontmatter
    frontmatter_yaml = yaml.dump(frontmatter_dict, default_flow_style=False, sort_keys=False)
    
    # Combine frontmatter + content
    result = f"---\n{frontmatter_yaml}---\n{content}"
    
    return result


def build_layer1_frontmatter(source_dir: Path, hierarchy_df: pd.DataFrame, 
                            batch_id: str, import_date: str, 
                            output_dir: Path) -> Dict:
    """
    Build and apply Layer 1 frontmatter to all files.
    
    Args:
        source_dir: Source directory with original files
        hierarchy_df: DataFrame from Task 2.1 with hierarchy mapping
        batch_id: Batch identifier
        import_date: Import date
        output_dir: Output directory for modified files
    
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Building Layer 1 frontmatter for {len(hierarchy_df)} files...")
    
    files_processed = 0
    files_skipped = 0
    
    for _, row in hierarchy_df.iterrows():
        file_name = row['file_name']
        source_path = source_dir / row['source_file_path']
        output_path = output_dir / file_name
        
        if not source_path.exists():
            logger.warning(f"File not found: {source_path}")
            files_skipped += 1
            continue
        
        try:
            # Build frontmatter
            hierarchy_dict = row.to_dict()
            frontmatter_dict = build_layer1_frontmatter_dict(
                hierarchy_dict,
                batch_id=batch_id,
                import_date=import_date,
                source_type='unknown'  # Will be updated in higher level
            )
            
            # Apply to file
            content_with_layer1 = apply_layer1_to_file(source_path, frontmatter_dict)
            
            # Save to output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content_with_layer1)
            
            files_processed += 1
            
        except Exception as e:
            logger.error(f"Error processing {file_name}: {str(e)}")
            files_skipped += 1
    
    logger.info(f"Layer 1 applied: {files_processed} processed, {files_skipped} skipped")
    
    return {
        'files_processed': files_processed,
        'files_skipped': files_skipped,
        'total': len(hierarchy_df)
    }


# Task 2.3: Validate Layer 1
# =========================================================================

def validate_frontmatter_structure(frontmatter_dict: Dict) -> Tuple[bool, List[str]]:
    """
    Validate Layer 1 frontmatter structure.
    
    Args:
        frontmatter_dict: Frontmatter dictionary to validate
    
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    required_fields = [
        'source', 'import-batch', 'import-date', 'status',
        'created-chronological', 'hierarchy', 'hierarchy-full'
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in frontmatter_dict:
            issues.append(f"Missing required field: {field}")
    
    # Validate date formats
    if 'import-date' in frontmatter_dict:
        date_str = frontmatter_dict['import-date']
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            issues.append(f"Invalid import-date format: {date_str}")
    
    if 'created-chronological' in frontmatter_dict:
        chrono = frontmatter_dict['created-chronological']
        if not re.match(r'^\d{4}-W\d{2}$', chrono):
            issues.append(f"Invalid chronological format: {chrono} (expected YYYY-WXX)")
    
    # Validate hierarchy
    if 'hierarchy' in frontmatter_dict:
        hierarchy = frontmatter_dict['hierarchy']
        if not isinstance(hierarchy, dict):
            issues.append("Hierarchy must be a dictionary")
    
    return len(issues) == 0, issues


def validate_layer1(source_dir: Path, output_dir: Path) -> Dict:
    """
    Validate Layer 1 frontmatter in all files.
    
    Args:
        source_dir: Directory with files containing Layer 1
        output_dir: Directory to save validation results
    
    Returns:
        Dictionary with validation statistics
    """
    logger.info("Validating Layer 1 integrity...")
    
    files_checked = 0
    files_passed = 0
    validation_issues = []
    
    for md_file in source_dir.glob("*.md"):
        files_checked += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            if not content.startswith('---'):
                validation_issues.append({
                    'file': md_file.name,
                    'status': 'FAIL',
                    'issue': 'No frontmatter found'
                })
                continue
            
            end_marker = content.find('\n---\n')
            if end_marker == -1:
                validation_issues.append({
                    'file': md_file.name,
                    'status': 'FAIL',
                    'issue': 'Frontmatter not properly closed'
                })
                continue
            
            yaml_str = content[4:end_marker]
            frontmatter_dict = yaml.safe_load(yaml_str)
            
            # Validate structure
            is_valid, issues = validate_frontmatter_structure(frontmatter_dict)
            
            if is_valid:
                files_passed += 1
                validation_issues.append({
                    'file': md_file.name,
                    'status': 'PASS',
                    'issue': None
                })
            else:
                validation_issues.append({
                    'file': md_file.name,
                    'status': 'FAIL',
                    'issue': '; '.join(issues[:3])
                })
        
        except Exception as e:
            validation_issues.append({
                'file': md_file.name,
                'status': 'ERROR',
                'issue': str(e)
            })
    
    # Save results
    pd.DataFrame(validation_issues).to_csv(
        output_dir / "layer1-validation-results.csv", index=False
    )
    
    logger.info(f"Validation complete: {files_passed}/{files_checked} passed")
    
    return {
        'files_checked': files_checked,
        'files_passed': files_passed,
        'files_failed': files_checked - files_passed
    }


if __name__ == '__main__':
    # For testing
    test_dir = Path('./test_files')
    output = Path('./stage_2_output')
    output.mkdir(exist_ok=True)
    
    # Create test manifest
    manifest = pd.DataFrame({
        'source_file': ['course_1/week_1/virtualization.md'],
        'file_size_kb': [25],
        'priority': [1]
    })
    
    # Map hierarchy
    hierarchy = map_file_to_hierarchy(manifest, 'lighthouse_labs', output)
    print(f"Hierarchy: {hierarchy}")
    
    # Build Layer 1
    # layer1_result = build_layer1_frontmatter(test_dir, hierarchy, 'test-batch', datetime.now().isoformat(), output)
    # print(f"Layer 1 result: {layer1_result}")
