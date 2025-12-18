#!/usr/bin/env python3
"""
Stage 1: Markdown Quality Assurance

Tasks:
- 1.1: Identify all source files
- 1.2: Lint markdown formatting
- 1.3: Normalize spelling & grammar
- 1.4: Extract existing metadata
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from spellchecker import SpellChecker
import yaml
import json
import logging

logger = logging.getLogger(__name__)


# Task 1.1: Identify Files
# =========================================================================

def identify_files(source_dir: Path, output_dir: Path) -> pd.DataFrame:
    """
    Identify all markdown files and create import manifest.
    
    Args:
        source_dir: Directory containing source markdown files
        output_dir: Directory to save manifest
    
    Returns:
        DataFrame with file manifest
    """
    logger.info(f"Scanning {source_dir} for markdown files...")
    
    files = []
    for md_file in Path(source_dir).rglob("*.md"):
        if md_file.is_file():
            size_kb = os.path.getsize(md_file) / 1024
            files.append({
                'source_file': str(md_file.relative_to(source_dir)),
                'full_path': str(md_file),
                'file_size_kb': round(size_kb, 2),
                'estimated_layer1_difficulty': 'auto',
                'estimated_tags': '7',  # Default estimate
                'priority': 1 if size_kb < 50 else 2  # Process smaller files first
            })
    
    # Sort by priority (smaller first) then by name
    files.sort(key=lambda x: (x['priority'], x['source_file']))
    
    df = pd.DataFrame(files)
    manifest_path = output_dir / "import-manifest.csv"
    df.to_csv(manifest_path, index=False)
    logger.info(f"Created manifest with {len(df)} files: {manifest_path}")
    
    return df


# Task 1.2: Lint Markdown
# =========================================================================

class MarkdownLinter:
    """Lint markdown files for formatting issues."""
    
    def __init__(self):
        self.issues = []
    
    def check_heading_hierarchy(self, lines: List[str]) -> List[str]:
        """Check that headings follow proper hierarchy (no skips)."""
        issues = []
        last_level = 0
        
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                # Allow jump from 0 to 1, but not 1 to 3
                if level > last_level + 1 and last_level > 0:
                    issues.append(f"Line {i}: Heading hierarchy skips level (H{last_level} → H{level})")
                last_level = level
        
        return issues
    
    def check_list_consistency(self, lines: List[str]) -> List[str]:
        """Check for consistent list formatting."""
        issues = []
        list_markers = set()
        
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith(('-', '*', '+')):
                marker = line.lstrip()[0]
                list_markers.add(marker)
                if len(list_markers) > 1:
                    issues.append(f"Line {i}: Mixed list markers {list_markers}")
        
        return issues
    
    def check_code_blocks(self, lines: List[str]) -> List[str]:
        """Check code block formatting."""
        issues = []
        in_code = False
        
        for i, line in enumerate(lines, 1):
            if line.startswith('```'):
                if in_code:
                    in_code = False
                else:
                    in_code = True
                    # Check if language is specified
                    if len(line.strip()) == 3:
                        logger.debug(f"Line {i}: Code block without language specified")
        
        if in_code:
            issues.append("Unclosed code block at end of file")
        
        return issues
    
    def check_trailing_spaces(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Find and fix trailing spaces."""
        issues = []
        fixed_lines = []
        
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip('\n'):
                issues.append(f"Line {i}: Trailing whitespace")
                fixed_lines.append(line.rstrip())
            else:
                fixed_lines.append(line)
        
        return issues, fixed_lines
    
    def check_extra_blank_lines(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Find and fix extra blank lines (>1 consecutive)."""
        issues = []
        fixed_lines = []
        prev_blank = False
        
        for i, line in enumerate(lines, 1):
            if line.strip() == '':
                if prev_blank:
                    issues.append(f"Line {i}: Extra blank line")
                    continue
                prev_blank = True
            else:
                prev_blank = False
            fixed_lines.append(line)
        
        return issues, fixed_lines
    
    def check_formatting_consistency(self, lines: List[str]) -> List[str]:
        """Check bold/italic formatting consistency."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for __bold__ vs **bold**
            if '__' in line and not line.startswith('__'):
                issues.append(f"Line {i}: Uses __bold__ instead of **bold**")
            # Check for _italic_ vs *italic*
            if re.search(r'[^*]_[a-zA-Z]', line):
                issues.append(f"Line {i}: Uses _italic_ instead of *italic*")
        
        return issues
    
    def lint_file(self, file_path: Path) -> Tuple[List[str], str]:
        """
        Lint a single markdown file.
        
        Returns:
            Tuple of (issues list, fixed content)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        all_issues = []
        
        # Run all checks
        all_issues.extend(self.check_heading_hierarchy(lines))
        all_issues.extend(self.check_list_consistency(lines))
        all_issues.extend(self.check_code_blocks(lines))
        all_issues.extend(self.check_formatting_consistency(lines))
        
        # Auto-fix trailing spaces and extra blanks
        trailing_issues, lines = self.check_trailing_spaces(lines)
        all_issues.extend(trailing_issues)
        
        extra_blank_issues, lines = self.check_extra_blank_lines(lines)
        all_issues.extend(extra_blank_issues)
        
        fixed_content = ''.join(lines)
        return all_issues, fixed_content


def lint_markdown(source_dir: Path, output_dir: Path) -> Dict:
    """
    Lint all markdown files and auto-fix where possible.
    
    Args:
        source_dir: Directory containing source files
        output_dir: Directory to save linting results
    
    Returns:
        Dictionary with linting statistics
    """
    logger.info("Linting markdown files...")
    
    linter = MarkdownLinter()
    linting_errors = []
    review_required = []
    files_checked = 0
    files_fixed = 0
    
    for md_file in source_dir.rglob("*.md"):
        if not md_file.is_file():
            continue
        
        files_checked += 1
        issues, fixed_content = linter.lint_file(md_file)
        
        if issues:
            # If there are auto-fixable issues, fix them
            if len(issues) <= 5:  # Small number of issues = probably auto-fixable
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                files_fixed += 1
                linting_errors.extend([
                    {'file': str(md_file.relative_to(source_dir)), 'issue': issue, 'fixed': True}
                    for issue in issues
                ])
            else:  # Complex issues require manual review
                review_required.append({
                    'file': str(md_file.relative_to(source_dir)),
                    'issues_count': len(issues),
                    'issues': '; '.join(issues[:3])  # First 3 issues
                })
    
    # Save results
    if linting_errors:
        pd.DataFrame(linting_errors).to_csv(output_dir / "linting-errors.csv", index=False)
    
    if review_required:
        pd.DataFrame(review_required).to_csv(output_dir / "linting-review-required.csv", index=False)
    
    logger.info(f"Linted {files_checked} files, fixed {files_fixed} files")
    
    return {
        'files_checked': files_checked,
        'files_fixed': files_fixed,
        'errors_found': len(linting_errors),
        'files_needing_review': len(review_required)
    }


# Task 1.3: Normalize Spelling & Grammar
# =========================================================================

def normalize_spelling(source_dir: Path, custom_dict: str, output_dir: Path) -> Dict:
    """
    Identify spelling and grammar issues.
    
    Args:
        source_dir: Directory containing markdown files
        custom_dict: Path to custom dictionary JSON
        output_dir: Directory to save results
    
    Returns:
        Dictionary with spelling statistics
    """
    logger.info("Checking spelling and grammar...")
    
    # Load custom dictionary
    spell = SpellChecker()
    if custom_dict and Path(custom_dict).exists():
        with open(custom_dict, 'r') as f:
            custom_terms = json.load(f)
        spell.word_list.update(custom_terms.get('technical_terms', []))
    
    spelling_issues = []
    grammar_issues = []
    
    for md_file in source_dir.rglob("*.md"):
        if not md_file.is_file():
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip code blocks and frontmatter
        lines = content.split('\n')
        in_frontmatter = lines[0].startswith('---')
        in_code = False
        
        for i, line in enumerate(lines, 1):
            if line.startswith('---'):
                in_frontmatter = not in_frontmatter
                continue
            if line.startswith('```'):
                in_code = not in_code
                continue
            
            if in_frontmatter or in_code:
                continue
            
            # Simple spell check
            words = re.findall(r'\b[a-z]+\b', line.lower())
            misspelled = spell.unknown(words)
            
            if misspelled:
                spelling_issues.append({
                    'file': str(md_file.relative_to(source_dir)),
                    'line': i,
                    'misspelled_words': '; '.join(misspelled),
                    'suggestions': '; '.join(
                        ['; '.join(spell.correction(word) if spell.correction(word) else word 
                                   for word in misspelled)]
                    )
                })
            
            # Basic grammar checks
            if re.search(r'[.!?] [a-z]', line):  # Lowercase after punctuation
                grammar_issues.append({
                    'file': str(md_file.relative_to(source_dir)),
                    'line': i,
                    'issue': 'Lowercase letter after punctuation',
                    'text': line[:80]
                })
    
    # Save results
    if spelling_issues:
        pd.DataFrame(spelling_issues).to_csv(output_dir / "spelling-issues.csv", index=False)
    
    if grammar_issues:
        pd.DataFrame(grammar_issues).to_csv(output_dir / "grammar-issues.csv", index=False)
    
    logger.info(f"Found {len(spelling_issues)} spelling and {len(grammar_issues)} grammar issues")
    
    return {
        'issues_found': len(spelling_issues) + len(grammar_issues),
        'spelling_issues': len(spelling_issues),
        'grammar_issues': len(grammar_issues)
    }


# Task 1.4: Extract Existing Metadata
# =========================================================================

def extract_existing_metadata(source_dir: Path, output_dir: Path) -> pd.DataFrame:
    """
    Extract and clean existing metadata from files.
    
    Args:
        source_dir: Directory containing markdown files
        output_dir: Directory to save results
    
    Returns:
        DataFrame with extracted metadata
    """
    logger.info("Extracting existing metadata...")
    
    metadata_list = []
    
    for md_file in source_dir.rglob("*.md"):
        if not md_file.is_file():
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_metadata = {
            'file_name': md_file.name,
            'existing_title': None,
            'created_date': None,
            'existing_tags': None,
            'metadata_format': 'None'
        }
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            end_marker = content.find('\n---\n')
            if end_marker != -1:
                try:
                    yaml_str = content[4:end_marker]
                    metadata = yaml.safe_load(yaml_str)
                    file_metadata['metadata_format'] = 'YAML'
                    if isinstance(metadata, dict):
                        file_metadata['existing_title'] = metadata.get('title')
                        file_metadata['created_date'] = metadata.get('date') or metadata.get('created_date')
                        file_metadata['existing_tags'] = metadata.get('tags')
                except:
                    pass
        
        # Check for Logseq properties format
        if '::' in content:
            props = re.findall(r'(\w+):: (.+?)(?:\n|$)', content)
            if props:
                file_metadata['metadata_format'] = 'Properties'
                for key, value in props:
                    if key.lower() == 'title':
                        file_metadata['existing_title'] = value
                    elif key.lower() in ['created_date', 'date']:
                        file_metadata['created_date'] = value
                    elif key.lower() == 'tags':
                        file_metadata['existing_tags'] = value
        
        # Extract title from first heading if not found
        if not file_metadata['existing_title']:
            heading_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if heading_match:
                file_metadata['existing_title'] = heading_match.group(1)
        
        metadata_list.append(file_metadata)
    
    df = pd.DataFrame(metadata_list)
    df.to_csv(output_dir / "existing-metadata.csv", index=False)
    logger.info(f"Extracted metadata from {len(df)} files")
    
    return df


if __name__ == '__main__':
    # For testing
    test_dir = Path('./test_files')
    output = Path('./stage_1_output')
    output.mkdir(exist_ok=True)
    
    manifest = identify_files(test_dir, output)
    lint_results = lint_markdown(test_dir, output)
    spell_results = normalize_spelling(test_dir, None, output)
    metadata_df = extract_existing_metadata(test_dir, output)
    
    print("Stage 1 QA Complete")
    print(f"Files: {manifest.shape[0]}")
    print(f"Linting: {lint_results}")
    print(f"Spelling: {spell_results}")
