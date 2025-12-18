#!/usr/bin/env python3
"""
Stage 4: Layer 3 Placeholder Generation

Tasks:
- 4.1: Detect potential connections
- 4.2: Build placeholder sections
- 4.3: Validate structure
"""

import re
from pathlib import Path
from typing import Dict, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def detect_layer3_connections(source_dir: Path, graph_structure: str = None,
                             output_dir: Path = None) -> Dict:
    """
    Detect potential Layer 3 connections for each file.
    
    Args:
        source_dir: Directory with markdown files
        graph_structure: Path to existing graph structure map
        output_dir: Output directory for candidates
    
    Returns:
        Dictionary with detection statistics
    """
    logger.info("Detecting Layer 3 connections...")
    
    candidates_list = []
    files_processed = 0
    
    for md_file in source_dir.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            candidates = {
                'file_name': md_file.name,
                'potential_prerequisites': [],
                'potential_enables': [],
                'potential_project_connections': [],
                'potential_goal_connections': [],
                'confidence': 'medium'
            }
            
            # Look for prerequisite keywords
            if any(word in content.lower() for word in ['prerequisite', 'requires', 'must', 'before']):
                candidates['confidence'] = 'high'
            
            # Look for enable keywords
            if any(word in content.lower() for word in ['enables', 'allows', 'foundation', 'basis']):
                candidates['potential_enables'].append('placeholder')
                candidates['confidence'] = 'high'
            
            candidates_list.append(candidates)
            files_processed += 1
            
        except Exception as e:
            logger.warning(f"Error detecting connections in {md_file.name}: {str(e)}")
    
    # Save results
    if output_dir:
        df = pd.DataFrame(candidates_list)
        df.to_csv(output_dir / "layer3-candidates.csv", index=False)
    
    logger.info(f"Connection detection complete: {files_processed} files analyzed")
    
    return {
        'files_analyzed': files_processed,
        'connections_found': sum(len(c.get('potential_prerequisites', [])) + 
                                len(c.get('potential_enables', []))
                                for c in candidates_list)
    }


def build_layer3_placeholders(source_dir: Path, candidates_file: Path,
                             output_dir: Path = None) -> Dict:
    """
    Build Layer 3 placeholder sections for all files.
    
    Args:
        source_dir: Directory with Layer 2 files
        candidates_file: CSV file with connection candidates
        output_dir: Output directory
    
    Returns:
        Dictionary with processing statistics
    """
    logger.info("Building Layer 3 placeholders...")
    
    candidates_df = pd.read_csv(candidates_file)
    files_processed = 0
    
    for _, row in candidates_df.iterrows():
        file_path = source_dir / row['file_name']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find where to insert placeholders (after tags, before main content)
            tags_marker = content.find('## Tags\n')
            if tags_marker == -1:
                # No tags section, insert after frontmatter
                if content.startswith('---'):
                    tags_marker = content.find('\n---\n') + 5
                else:
                    tags_marker = 0
            else:
                # Skip past tags section to next heading
                next_heading = content.find('\n## ', tags_marker + 8)
                if next_heading == -1:
                    next_heading = content.find('\n# ', tags_marker + 8)
                tags_marker = next_heading if next_heading != -1 else len(content)
            
            # Build placeholder sections
            placeholder_section = """
## Prerequisites
- [ ] [[]]  # Will you populate these?
- [ ] [[]]

## Enables
- [ ] [[]]  # Concepts this material helps you learn
- [ ] [[]]

## Project Connections
- [ ] [[]]  # Relevant projects or applications

## Goal Connections
- [ ] [[]]  # Career goals this supports

## See Also
Connection candidates for your consideration:
- [[]]  # Related topics from similar content

"""
            
            # Insert placeholders
            new_content = (content[:tags_marker] + placeholder_section + 
                          content[tags_marker:])
            
            # Write back
            output_path = output_dir / row['file_name'] if output_dir else file_path
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            files_processed += 1
            
        except Exception as e:
            logger.error(f"Error building placeholders for {row['file_name']}: {str(e)}")
    
    logger.info(f"Layer 3 placeholders created for {files_processed} files")
    
    return {
        'files_processed': files_processed,
        'total': len(candidates_df)
    }


def validate_layer3(source_dir: Path, output_dir: Path = None) -> Dict:
    """
    Validate Layer 3 placeholder structure in all files.
    
    Args:
        source_dir: Directory with files
        output_dir: Output directory for results
    
    Returns:
        Dictionary with validation statistics
    """
    logger.info("Validating Layer 3 structure...")
    
    files_checked = 0
    files_passed = 0
    validation_issues = []
    
    required_sections = ['Prerequisites', 'Enables', 'Project Connections', 'Goal Connections']
    
    for md_file in source_dir.glob("*.md"):
        files_checked += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_sections = []
            for section in required_sections:
                if f"## {section}" not in content:
                    missing_sections.append(section)
            
            if not missing_sections:
                files_passed += 1
                status = 'PASS'
                issues = None
            else:
                status = 'FAIL'
                issues = f"Missing sections: {'; '.join(missing_sections)}"
            
            validation_issues.append({
                'file': md_file.name,
                'status': status,
                'issues': issues
            })
            
        except Exception as e:
            validation_issues.append({
                'file': md_file.name,
                'status': 'ERROR',
                'issues': str(e)
            })
    
    # Save results
    if output_dir:
        pd.DataFrame(validation_issues).to_csv(
            output_dir / "layer3-validation-results.csv", index=False
        )
    
    logger.info(f"Layer 3 validation: {files_passed}/{files_checked} passed")
    
    return {
        'files_checked': files_checked,
        'files_passed': files_passed,
        'files_failed': files_checked - files_passed
    }


if __name__ == '__main__':
    test_dir = Path('./test_files')
    output = Path('./stage_4_output')
    output.mkdir(exist_ok=True)
    
    detect_result = detect_layer3_connections(test_dir, None, output)
    print(f"Detection result: {detect_result}")
